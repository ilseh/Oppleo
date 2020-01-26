import logging
import os

PROD = 'production'


class GenericUtil(object):

    @staticmethod
    def isProd():
        env_name = os.getenv('CARCHARGING_ENV')
        return env_name.lower() == PROD

    @staticmethod
    def getMeasurementDevice():
        return os.getenv('ENERGY_DEVICE_ID')

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
