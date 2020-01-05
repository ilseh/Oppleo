import logging
import os
import sys
import time

from nl.carcharging.models.EnergyDeviceMeasureModel import EnergyDeviceMeasureModel
from nl.carcharging.models.SessionModel import SessionModel
from nl.carcharging.utils.GenericUtil import GenericUtil
from nl.carcharging.views.SessionView import session_schema

try:
    import RPi.GPIO as GPIO
    from mfrc522 import SimpleMFRC522
except RuntimeError:
    logging.debug('Assuming dev env')

from apscheduler.schedulers.background import BackgroundScheduler
from injector import inject, Injector
from service import Service

from nl.carcharging.config import Logger

from nl.carcharging.services.LedLighter import LedLighter
from nl.carcharging.services.RfidReader import RfidReader
from nl.carcharging.utils.EnergyUtil import EnergyUtil

PROCESS_NAME = 'rfid_reader'
LOG_FILE = '/tmp/%s.log' % PROCESS_NAME

MAX_SECONDS_INTERVAL_CHARGING = 20

scheduler = BackgroundScheduler()

# TODO: make pid_dir configurable
PID_DIR = '/tmp/'
SECONDS_IN_HOUR = 60 * 60


class LedLightHandler(Service):

    @inject
    def __init__(self, energy_util: EnergyUtil):
        super(LedLightHandler, self).__init__(PROCESS_NAME, pid_dir=PID_DIR)
        self.ledlighterAvailable = LedLighter(LedLighter.LED_GREEN)
        self.ledlighterReady = LedLighter(LedLighter.LED_RED, LedLighter.LED_GREEN)
        self.ledlighterCharging = LedLighter(LedLighter.LED_BLUE)
        self.energy_util = energy_util
        self.current_light = None
        self.previous_light = None

    def run(self):
        # TODO: Just started up. Check if there was a session in progress.
        #  Retrieved last session that was stored and check if it was ended or not.
        #  I suppose we need to link laadpaal to this instance...
        device = GenericUtil.getMeasurementDevice()
        self.logger.info("Starting rfid reader for device %s" % device)

        self.current_light = self.ledlighterAvailable
        self.current_light.on(5)

        scheduler.add_job(id="check_is_charging",
                          func=self.handle_charging, args=[device],
                          trigger="interval", seconds=20)
        scheduler.start()

        reader = RfidReader()
        while not self.got_sigterm():
            self.logger.debug("Getting ready to read rfid...")
            rfid, text = reader.read()
            self.logger.debug("Rfid id and text: %d - %s" % (rfid, text))

            # TODO: check if rfid wants to start or stop session (toggle). We check by checking
            #  if rfid has an open session or not.
            latest_session = SessionModel.get_latest_rfid_session(rfid)

            start_session = False
            data = {"rfid": rfid}
            # If there is no session at all yet for rfid or the end_value is set, we need to start new session.
            if latest_session is None or latest_session.end_value:
                data['start_value'] = self.energy_util.getMeasurementValue(device)['kw_total']
                session = SessionModel(data)
                session.save()
                ser_data = session_schema.dump(session)
                start_session = True
                self.logger.debug("Starting new charging session for rfid %s" % rfid)
            else:
                latest_session.end_value = self.energy_util.getMeasurementValue(device)['kw_total']
                latest_session.save()
                ser_data = session_schema.dump(latest_session)
                self.logger.debug("Stopping charging session for rfid %s" % rfid)


            self.turn_current_light_off()

            # TODO: if open session than toggle session off (and stop the electricity) and set light to available again.
            #  If no session open, we get a new session and set light to ready (and start electricity flow and ligth to charging).
            if start_session:
                self.current_light = self.ledlighterReady
            else:
                self.current_light = self.ledlighterAvailable
            self.current_light.on(5)

            time.sleep(2)
        else:
            self.logger.info("Stopping RfidReader")
            self.stop()

    def turn_current_light_off(self):
        self.current_light.off()
        # if self.current_light == self.ledlighterCharging:
        #     self.current_light.pulse_stop()
        # else:
        #     self.current_light.off()

    def stop(self, block=False):
        self.ledlighterAvailable.off()
        self.ledlighterAvailable.cleanup()
        self.ledlighterReady.off()
        self.ledlighterAvailable.cleanup()

    def handle_charging(self, device):
        last_two_measures = EnergyDeviceMeasureModel().get_last_n_saved(device, 2)
        diff_last_two_measures_saved = last_two_measures[0].created_at - last_two_measures[1].created_at
        # Get dummy measure to get current datetime which we can use to see if charging is going pn.
        current_date_time = EnergyDeviceMeasureModel()
        current_date_time.set({})
        diff_now_and_last_saved_session = current_date_time.created_at - last_two_measures[0].created_at
        # It is charging, let blue light pulse.
        if diff_now_and_last_saved_session.seconds <= MAX_SECONDS_INTERVAL_CHARGING \
                and diff_last_two_measures_saved.seconds <= MAX_SECONDS_INTERVAL_CHARGING:
            self.logger.debug("Device is currently charging")
            if self.current_light != self.ledlighterCharging:
                self.previous_light = self.current_light
                self.turn_current_light_off()
                self.current_light = self.ledlighterCharging
                self.current_light.on(50)
                # self.current_light.pulse()
        #         self.logger.debug("Blue light is pulsing to indicate charging")
        else:
            self.logger.debug("Not charging")
        #     # Not charging. If it was charging, set light back to previous light
        #     if self.current_light == self.ledlighterCharging:
        #         self.logger.debug("Charging is stopped, setting back previous light %s" % self.previous_light)
        #         self.turn_current_light_off()
        #         self.current_light = self.previous_light
        #         self.current_light.on(5)



def main():
    Logger.init_log(PROCESS_NAME, LOG_FILE)

    env_name = os.getenv('CARCHARGING_ENV')

    logger = logging.getLogger(PROCESS_NAME)
    logger.info('Starting for environment %s' % env_name)

    if len(sys.argv) != 2:
        sys.exit('Invalid COMMAND %s, give an argument, ie \'start\'' % sys.argv[0])

    cmd = sys.argv[1].lower()

    logger.info('Received command: %s' % cmd)

    injector = Injector()
    service = injector.get(LedLightHandler)


    if cmd == 'start':
        service.start()
        logger.debug('started')
    elif cmd == 'debug':
        service.run()
    elif cmd == 'stop':
        stopped = service.stop()
        if not stopped:
            sys.exit('Could not stop service, trying kill instead')
    elif cmd == 'kill':
        # GPIO.cleanup()
        stopped = service.kill()
    elif cmd == 'status':
        if service.is_running():
            print("Service is running.")
        else:
            print("Service is not running.")
    else:
        sys.exit('Unknown command "%s".' % cmd)


if __name__ == '__main__':
    main()
