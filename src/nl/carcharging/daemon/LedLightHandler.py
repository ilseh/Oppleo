import logging
import os
import sys
import time
from datetime import datetime

from nl.carcharging.models.EnergyDeviceMeasureModel import EnergyDeviceMeasureModel
from nl.carcharging.models.RfidModel import RfidModel
from nl.carcharging.models.SessionModel import SessionModel
from nl.carcharging.services.Charger import Charger
from nl.carcharging.utils.GenericUtil import GenericUtil

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

class NotAuthorizedException(Exception):
    pass

class LedLightHandler(Service):

    @inject
    def __init__(self, energy_util: EnergyUtil, charger: Charger):
        super(LedLightHandler, self).__init__(PROCESS_NAME, pid_dir=PID_DIR)

        self.energy_util = energy_util
        self.charger = charger

        self.ledlighterAvailable = LedLighter(LedLighter.LED_GREEN)
        self.ledlighterReady = LedLighter(LedLighter.LED_RED, LedLighter.LED_GREEN)
        self.ledlighterCharging = LedLighter(LedLighter.LED_BLUE)
        self.ledlighterError = LedLighter(LedLighter.LED_RED)

        self.current_light = None
        self.previous_light = None

    def error_status(self):
        self.current_light = self.ledlighterError
        self.current_light.on(80)

    def run(self):

        device = GenericUtil.getMeasurementDevice()

        try:
            scheduler.add_job(id="check_is_charging",
                              func=self.try_handle_charging, args=[device],
                              trigger="interval", seconds=10)
            scheduler.start()
        except Exception as ex:
            self.logger.error("Could not start scheduler to check if charging is active: %s" % ex)
            self.error_status()

        try:
            self.read_rfid_loop(device)
        except Exception as ex:
            self.logger.error("Could not execute read_rfid %s" % ex)
            self.error_status()


    def is_authorized(self, rfid):

        authorized = False

        try:
            rfid_data = RfidModel.get_one(rfid)
            if rfid_data is None:
                self.logger.warn("Unknown rfid offered. Access denied and rfid value saved in db.")
                new_rfid_entry = RfidModel({"rfid": rfid})
                new_rfid_entry.save()
            else:
                authorized = rfid_data.allow
                self.logger.info("Rfid %s offered. Access %s" % (rfid, authorized))
                rfid_data.last_used_at = datetime.now()
                rfid_data.save()
        except Exception as ex:
            self.logger.error("Could not authorize %s %s" % (rfid, ex))

        return authorized

    def temp_switch_to_light(self, light, brightness, duration):
        self.previous_light = self.current_light
        self.current_light.off()
        self.current_light = light
        self.current_light.on(brightness)
        time.sleep(duration)
        self.current_light.off()
        self.current_light = self.previous_light
        self.current_light.on(self.current_light.brightness)

    def read_rfid_loop(self, device):
        # TODO: Just started up. Check if there was a session in progress.
        #  Retrieved last session that was stored and check if it was ended or not.
        #  I suppose we need to link laadpaal to this instance...
        self.logger.info("Starting rfid reader for device %s" % device)

        self.current_light = self.ledlighterAvailable
        self.current_light.on(5)

        reader = RfidReader()
        while not self.got_sigterm():
           try:
               self.read_rfid(reader, device)
           except Exception as ex:
               self.logger.error("Could not execute run_rfid: %s" % ex)
               self.temp_switch_to_light(self.ledlighterError, 90, 3)

           time.sleep(2)
        else:
            self.logger.info("Stopping RfidReader")
            self.stop()

    def read_rfid(self, reader, device):
        rfid, text = reader.read()
        self.logger.debug("Rfid id and text: %d - %s" % (rfid, text))

        if not self.is_authorized(rfid):
            raise NotAuthorizedException("Unauthorized rfid %s" % rfid)

        latest_session = SessionModel.get_latest_rfid_session(rfid)

        start_session = False
        data_for_session = {"rfid": rfid}
        # If there is no session at all yet for rfid or the end_value is set, we need to start new session.
        if latest_session is None or latest_session.end_value:
            data_for_session['start_value'] = self.energy_util.getMeasurementValue(device)['kw_total']
            session = SessionModel(data_for_session)
            session.save()
            start_session = True
            self.logger.debug("Starting new charging session for rfid %s" % rfid)
        else:
            latest_session.end_value = self.energy_util.getMeasurementValue(device)['kw_total']
            latest_session.save()
            self.logger.debug("Stopping charging session for rfid %s" % rfid)

        self.turn_current_light_off()

        # TODO: if open session than toggle session off (and stop the electricity) and set light to available again.
        #  If no session open, we get a new session and set light to ready (and start electricity flow and ligth to charging).
        if start_session:
            self.charger.start()
            self.current_light = self.ledlighterReady
        else:
            self.charger.stop()
            self.current_light = self.ledlighterAvailable
        self.current_light.on(5)


    def turn_current_light_off(self):
        if self.current_light == self.ledlighterCharging:
            self.current_light.pulse_stop()
        else:
            self.current_light.off()

    def stop(self, block=False):
        lights = {self.ledlighterAvailable, self.ledlighterReady, self.ledlighterError}
        for light in lights:
            light.off()
            light.cleanup()

    def try_handle_charging(self, device):
        try:
            self.handle_charging(device)
        except Exception as ex:
            self.error_status()

    def handle_charging(self, device):
        last_two_measures = EnergyDeviceMeasureModel().get_last_n_saved(device, 2)
        diff_last_two_measures_saved = last_two_measures[0].created_at - last_two_measures[1].created_at
        # Get dummy measure to get current datetime which we can use to see if charging is going on.
        current_date_time = EnergyDeviceMeasureModel()
        current_date_time.set({})
        diff_now_and_last_saved_session = current_date_time.created_at - last_two_measures[0].created_at
        if self.is_car_charging(diff_now_and_last_saved_session, diff_last_two_measures_saved):
            self.logger.debug("Device is currently charging")
            if self.current_light != self.ledlighterCharging:
                self.previous_light = self.current_light
                self.turn_current_light_off()
                self.logger.debug("Prevous light off, setting charging light")
                self.current_light = self.ledlighterCharging
                self.logger.debug('Start charging light pulse')
                self.current_light.pulse()
        else:
            self.logger.debug("Not charging")
            # Not charging. If it was charging, set light back to previous light
            if self.current_light == self.ledlighterCharging:
                self.logger.debug("Charging is stopped, setting back previous light %s" % self.previous_light)
                self.turn_current_light_off()
                self.current_light = self.previous_light
                self.current_light.on(5)

    def is_car_charging(self, diff_now_and_last_saved_session, diff_last_two_measures_saved):
        return diff_now_and_last_saved_session.seconds <= MAX_SECONDS_INTERVAL_CHARGING \
               and diff_last_two_measures_saved.seconds <= MAX_SECONDS_INTERVAL_CHARGING


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
