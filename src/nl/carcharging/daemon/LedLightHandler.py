import logging
import os
import sys
import time

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

PROCESS_NAME = 'rfid_reader'
LOG_FILE = '/tmp/%s.log' % PROCESS_NAME


scheduler = BlockingScheduler()

# TODO: make pid_dir configurable
PID_DIR = '/tmp/'
SECONDS_IN_HOUR = 60 * 60


class LedLightHandler(Service):

    @inject
    def __init__(self):
        super(LedLightHandler, self).__init__(PROCESS_NAME, pid_dir=PID_DIR)
        self.ledlighterAvailable = LedLighter(LedLighter.LED_GREEN)
        self.ledlighterReady = LedLighter(LedLighter.LED_RED, LedLighter.LED_GREEN)

    def run(self):
        # TODO: Just started up. Check if there was a session in progress.
        #  Retrieved last session that was stored and check if it was ended or not.

        reader = RfidReader()
        while not self.got_sigterm():
            self.ledlighterReady.on(5)
            rfid, text = reader.read()
            self.logger.debug("Rfid id and text: %d - %s" % (rfid, text))

            self.ledlighterReady.off()
            self.ledlighterAvailable.on(5)
            time.sleep(5)
            self.ledlighterAvailable.off()

            # TODO: check if rfid wants to start or stop session (toggle). We check by checking
            #  if rfid has an open session or not.

            # TODO: if open session than toggle session off (and stop the electricity) and set light to available again.
            #  If no session open, we get a new session and set light to ready (and start electricity flow and ligth to charging).

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
