import logging
import os

from nl.oppleo.config.OppleoConfig import OppleoConfig

PROD = 'production'


class GenericUtil(object):

    @staticmethod
    def isProd():
        if OppleoConfig.ini_settings is None:
            OppleoConfig.loadConfig()
        return OppleoConfig.PRODUCTION
        # env_name = os.getenv('oppleo_ENV')
        # return env_name.lower() == PROD

    # deprecated - use OppleoConfig.ENERGY_DEVICE_ID directly
    @staticmethod
    def getMeasurementDevice():
        # Configured in nl.cargarging.config.carcharger.ini file
        if OppleoConfig.ini_settings is None:
            OppleoConfig.loadConfig()
        return OppleoConfig.ENERGY_DEVICE_ID
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
