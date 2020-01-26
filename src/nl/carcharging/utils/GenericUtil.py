import logging
import os

from nl.carcharging.config.WebAppConfig import WebAppConfig

PROD = 'production'


class GenericUtil(object):

    @staticmethod
    def isProd():
        if WebAppConfig.ini_settings is None:
            WebAppConfig.loadConfig()
        return WebAppConfig.PRODUCTION
        # env_name = os.getenv('CARCHARGING_ENV')
        # return env_name.lower() == PROD

    @staticmethod
    def getMeasurementDevice():
        # Configured in nl.cargarging.config.carcharger.ini file
        if WebAppConfig.ini_settings is None:
            WebAppConfig.loadConfig()
        return WebAppConfig.ENERGY_DEVICE_ID
        #return os.getenv('ENERGY_DEVICE_ID')

    @staticmethod
    def importGpio():
        GPIO = None
        try:
            import RPi.GPIO as PIO
            GPIO = PIO
        except RuntimeError:
            logging.debug('Can not import gpio, Assuming dev env')

        return GPIO

    @staticmethod
    def importMfrc522():
        try:
            from mfrc522 import SimpleMFRC522
        except RuntimeError:
            logging.debug('Can not import mfrc522, Assuming dev env')
