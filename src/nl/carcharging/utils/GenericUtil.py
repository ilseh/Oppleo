#import os
from nl.carcharging.config.WebAppConfig import WebAppConfig

# PROD = 'production'

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
