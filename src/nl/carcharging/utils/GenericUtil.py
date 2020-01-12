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
