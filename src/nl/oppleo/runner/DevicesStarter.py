import logging
import os
import sys

from injector import Injector

from nl.oppleo.config import Logger
from nl.oppleo.daemon.LedLightHandler import LedLightHandler, PROCESS_NAME as LedLight_PROCESS_NAME
from nl.oppleo.daemon.MeasureElectricityUsage import MeasureElectricityUsage, PROCESS_NAME as MeasureElectricity_PROCESS_NAME

PROCESS_NAME = 'carcharger-devices'
LOG_FILE = '/tmp/%s.log' % PROCESS_NAME


def main():
    Logger.init_log(PROCESS_NAME, LOG_FILE, [LedLight_PROCESS_NAME, MeasureElectricity_PROCESS_NAME])

    env_name = os.getenv('oppleo_ENV')

    logger = logging.getLogger(PROCESS_NAME)
    logger.info('Starting for environment %s' % env_name)

    if len(sys.argv) != 2:
        sys.exit('Invalid COMMAND %s, give an argument, ie \'start\'' % sys.argv[0])

    cmd = sys.argv[1].lower()

    logger.info('Received command: %s' % cmd)

    injector = Injector()
    ledlight_handler = injector.get(LedLightHandler)
    measure_electric_usage_handler = injector.get(MeasureElectricityUsage)

    handlers = [ledlight_handler, measure_electric_usage_handler]

    if cmd == 'start':
        for handler in handlers:
            handler.start()
        logger.debug('handlers started')
    elif cmd == 'debug':
        for handler in handlers:
            handler.run()
    elif cmd == 'stop':
        for handler in handlers:
            stopped = handler.stop()
            if not stopped:
                sys.exit('Could not stop service, try kill instead')
    elif cmd == 'kill':
        # GPIO.cleanup()
        for handler in handlers:
            handler.kill()
    elif cmd == 'status':
        for handler in handlers:
            if handler.is_running():
                print("Service %s is running." % handler.__class__)
            else:
                print("Service %s is not running." % handler.__class__)
    else:
        sys.exit('Unknown command "%s".' % cmd)


if __name__ == '__main__':
    main()
