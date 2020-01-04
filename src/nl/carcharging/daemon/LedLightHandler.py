import logging
import os
import sys
import time

from nl.carcharging.models.SessionModel import SessionModel
from nl.carcharging.utils.GenericUtil import GenericUtil
from nl.carcharging.views.SessionView import session_schema

try:
    import RPi.GPIO as GPIO
    from mfrc522 import SimpleMFRC522
except RuntimeError:
    logging.debug('Assuming dev env')

from apscheduler.schedulers.blocking import BlockingScheduler
from injector import inject, Injector
from service import Service

from nl.carcharging.config import Logger

from nl.carcharging.services.LedLighter import LedLighter
from nl.carcharging.services.RfidReader import RfidReader
from nl.carcharging.utils.EnergyUtil import EnergyUtil

PROCESS_NAME = 'rfid_reader'
LOG_FILE = '/tmp/%s.log' % PROCESS_NAME


scheduler = BlockingScheduler()

# TODO: make pid_dir configurable
PID_DIR = '/tmp/'
SECONDS_IN_HOUR = 60 * 60


class LedLightHandler(Service):

    @inject
    def __init__(self, energy_util: EnergyUtil):
        super(LedLightHandler, self).__init__(PROCESS_NAME, pid_dir=PID_DIR)
        self.ledlighterAvailable = LedLighter(LedLighter.LED_GREEN)
        self.ledlighterReady = LedLighter(LedLighter.LED_RED, LedLighter.LED_GREEN)
        self.energy_util = energy_util

    def run(self):
        # TODO: Just started up. Check if there was a session in progress.
        #  Retrieved last session that was stored and check if it was ended or not.
        #  I suppose we need to link laadpaal to this instance...
        device = GenericUtil.getMeasurementDevice()
        self.logger.info("Starting rfid reader for device %s" % device)

        current_light = self.ledlighterAvailable
        current_light.on(5)


        reader = RfidReader()
        while not self.got_sigterm():
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
            else:
                latest_session.end_value = self.energy_util.getMeasurementValue(device)['kw_total']
                latest_session.save()
                ser_data = session_schema.dump(latest_session)


            current_light.off()

            # TODO: if open session than toggle session off (and stop the electricity) and set light to available again.
            #  If no session open, we get a new session and set light to ready (and start electricity flow and ligth to charging).
            if start_session:
                current_light = self.ledlighterReady
            else:
                current_light = self.ledlighterAvailable
            current_light.on(5)

            time.sleep(2)
        else:
            self.logger.info("Stopping RfidReader")
            self.stop()

    def stop(self, block=False):
        self.ledlighterAvailable.off()
        self.ledlighterAvailable.cleanup()
        self.ledlighterReady.off()
        self.ledlighterAvailable.cleanup()


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
