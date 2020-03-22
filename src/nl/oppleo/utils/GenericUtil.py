import logging
import os

from nl.oppleo.config.OppleoSystemConfig import OppleoSystemConfig
from nl.oppleo.config.OppleoConfig import OppleoConfig

PROD = 'Production'

oppleoSystemConfig = OppleoSystemConfig()

class GenericUtil(object):

    @staticmethod
    def isProd():
        return oppleoSystemConfig.ENV == PROD
        # env_name = os.getenv('oppleo_ENV')
        # return env_name.lower() == PROD

    # deprecated - use OppleoConfig.chargerName directly
    @staticmethod
    def getMeasurementDevice():
        # Configured in nl.cargarging.config.carcharger.ini file
        oppleoConfig = OppleoConfig()
        return oppleoConfig.chargerName
        #return os.getenv('ENERGY_DEVICE_ID')

    @staticmethod
    def importGpio():
        GPIO = None
        try:
            import RPi.GPIO as PIO
            GPIO = PIO
        except RuntimeError:
            logging.debug('Can not import gpio, Assuming dev env')
        except ModuleNotFoundError:
            logging.debug('Can not import gpio, Assuming dev env')

        return GPIO

    @staticmethod
    def importMfrc522():
        try:
            from mfrc522 import SimpleMFRC522
        except RuntimeError:
            logging.debug('Can not import mfrc522, Assuming dev env')
        except ModuleNotFoundError:
            logging.debug('Can not import mfrc522, Assuming dev env')
