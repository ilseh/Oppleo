import logging
import os
import sys
import time

from apscheduler.schedulers.blocking import BlockingScheduler
from injector import inject, Injector
from service import Service

from nl.carcharging.config import Logger

from nl.carcharging.services.LedLighter import LedLighter

PROCESS_NAME = 'rfid_reader'
LOG_FILE = '/tmp/%s.log' % PROCESS_NAME


scheduler = BlockingScheduler()

# TODO: make pid_dir configurable
PID_DIR = '/tmp/'
SECONDS_IN_HOUR = 60 * 60


class RfidReader(Service):

    @inject
    def __init__(self):
        super(RfidReader, self).__init__(PROCESS_NAME, pid_dir=PID_DIR)
        self.ledlighter = LedLighter(LedLighter.LED_BLUE)

    def run(self):
        self.ledlighter.pulse()
        while not self.got_sigterm():
            time.sleep(20)
            self.ledlighter.stop()
        else:
            self.logger.info("Stopping RfidReader")

    def stop(self, block=False):
        self.ledlighter.stop()


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
    service = injector.get(RfidReader)

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
