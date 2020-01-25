
from configparser import ConfigParser, NoSectionError, NoOptionError, ExtendedInterpolation
import logging
import os
from nl.carcharging.config import Logger

"""
 First init the Logger, then load the config
"""

# 
class WebAppConfig(object):
    # ini file param names
    INI_MAIN = 'CarChargerWebApp'
    # Params are all read as lowercase by ConfigParser (!)
    INI_TARGET_PARAM = 'activeTarget'
    INI_ENV_PARAM = 'carChargingEnv'

    INI_DATABASE_URL = 'DATABASE_URL'
    INI_ENERGY_DEVICE_ID = 'ENERGY_DEVICE_ID'
    INI_PYTHONPATH = 'PYTHONPATH'
    INI_SQLALCHEMY_DATABASE_URI = 'SQLALCHEMY_DATABASE_URI'

    INI_IS_PROD = 'Production'

    INI_DEBUG = 'DEBUG'
    INI_TESTING = 'TESTING'

    # ini content
    ini_settings = None

    # INI params
    DATABASE_URL = None
    ENERGY_DEVICE_ID = 'NONE'
    PYTHONPATH = ''
    SQLALCHEMY_DATABASE_URI = None

    # INI params
    PRODUCTION = False
    DEBUG = True
    TESTING = False

    login_manager = None
    flaskApp = None
    flaskAppSocketIO = None

    sqlalchemy_engine = None
    sqlalchemy_session_factory = None
    sqlalchemy_session = None

    # WebAppConfig Logger
    logger = None
    PROCESS_NAME = 'PythonProc'
    LOG_FILE = '/tmp/%s.log' % PROCESS_NAME

    @staticmethod
    def loadConfig(filename='carcharger.ini'):
        if WebAppConfig.logger is None:
            WebAppConfig.initLogger()
        WebAppConfig.logger.debug('Initializing WebApp')
        # Load the ini file
        WebAppConfig.ini_settings = ConfigParser()
        # Allow dynamic fields in the config ini file
        WebAppConfig.ini_settings._interpolation = ExtendedInterpolation()
        #WebAppConfig.ini_settings.read(filename)
        try:
            # The absolute dir the script is in
            configFile = os.path.join(os.path.dirname(os.path.realpath(__file__)), filename)
            WebAppConfig.logger.debug('Looking for ini file ' + configFile)
            print('Looking for ini file ' + configFile)
            WebAppConfig.ini_settings.read_file(open(configFile, "r"))
        except FileNotFoundError:
            WebAppConfig.logger.debug('Ini file not found.')
            return

        # Read the ini file
        mainSectionDict = WebAppConfig.configSectionMap(WebAppConfig.INI_MAIN)
        if mainSectionDict is None:
            return

        # Which target is active?
        if not WebAppConfig.INI_TARGET_PARAM.lower() in mainSectionDict:
            WebAppConfig.logger.error('Ini file ERROR: No ' + WebAppConfig.INI_TARGET_PARAM + ' in ' + WebAppConfig.INI_MAIN)
        else:
            targetSectionName = mainSectionDict[WebAppConfig.INI_TARGET_PARAM.lower()]
            targetSectionDict = WebAppConfig.configSectionMap(targetSectionName)

            if not WebAppConfig.INI_DATABASE_URL.lower() in targetSectionDict:
                WebAppConfig.logger.error('Ini file ERROR: No ' + WebAppConfig.INI_DATABASE_URL + ' in ' + targetSectionName)
            WebAppConfig.DATABASE_URL = targetSectionDict[WebAppConfig.INI_DATABASE_URL.lower()]

            if not WebAppConfig.INI_ENERGY_DEVICE_ID.lower() in targetSectionDict:
                WebAppConfig.logger.error('Ini file ERROR: No ' + WebAppConfig.INI_ENERGY_DEVICE_ID + ' in ' + targetSectionName)
            WebAppConfig.ENERGY_DEVICE_ID = targetSectionDict[WebAppConfig.INI_ENERGY_DEVICE_ID.lower()]

            if not WebAppConfig.INI_PYTHONPATH.lower() in targetSectionDict:
                WebAppConfig.logger.error('Ini file ERROR: No ' + WebAppConfig.INI_PYTHONPATH + ' in ' + targetSectionName)
            WebAppConfig.PYTHONPATH = targetSectionDict[WebAppConfig.INI_PYTHONPATH.lower()]

            if not WebAppConfig.INI_SQLALCHEMY_DATABASE_URI.lower() in targetSectionDict:
                WebAppConfig.logger.error('Ini file ERROR: No ' + WebAppConfig.INI_SQLALCHEMY_DATABASE_URI + ' in ' + targetSectionName)
            WebAppConfig.SQLALCHEMY_DATABASE_URI = targetSectionDict[WebAppConfig.INI_SQLALCHEMY_DATABASE_URI.lower()]


        # Which environment is active?
        mainSectionDict = WebAppConfig.configSectionMap(WebAppConfig.INI_MAIN)

        if not WebAppConfig.INI_ENV_PARAM.lower() in mainSectionDict:
            WebAppConfig.logger.error('Ini file ERROR: No ' + WebAppConfig.INI_ENV_PARAM + ' in ' + WebAppConfig.INI_MAIN)
        else: 
            envSectionName = mainSectionDict[WebAppConfig.INI_ENV_PARAM.lower()]
            WebAppConfig.PRODUCTION = ( envSectionName.lower() == WebAppConfig.INI_IS_PROD )
            envSectionDict = WebAppConfig.configSectionMap(envSectionName)

            if not WebAppConfig.INI_DEBUG.lower() in envSectionDict:
                WebAppConfig.logger.error('Ini file ERROR: No ' + WebAppConfig.INI_DEBUG + ' in ' + envSectionDict)
            WebAppConfig.DEBUG = envSectionDict[WebAppConfig.INI_DEBUG.lower()]

            if not WebAppConfig.INI_TESTING.lower() in envSectionDict:
                WebAppConfig.logger.error('Ini file ERROR: No ' + WebAppConfig.INI_TESTING + ' in ' + envSectionDict)
            WebAppConfig.TESTING = envSectionDict[WebAppConfig.INI_TESTING.lower()]


    @staticmethod
    def initLogger(process_name='PythonProc'):
        WebAppConfig.PROCESS_NAME = process_name
        WebAppConfig.LOG_FILE = '/tmp/%s.log' % WebAppConfig.PROCESS_NAME
        Logger.init_log(WebAppConfig.PROCESS_NAME, WebAppConfig.LOG_FILE)
        WebAppConfig.logger = logging.getLogger('nl.carcharging.webapp.WebApp')


    @staticmethod
    def configSectionMap(section):
        dict1 = {}
        try:
            options = WebAppConfig.ini_settings.options(section)
        except NoSectionError:
            WebAppConfig.logger.error('Ini file Section: %s not found in ini file' % section)
            return

        for option in options:
            try:
                dict1[option] = WebAppConfig.ini_settings.get(section, option)
                if dict1[option] == -1:
                    WebAppConfig.logger.debug('Ini file excskip %s' % option)
            except NoOptionError:
                WebAppConfig.logger.error('Ini file exception on %s!' % option)
                dict1[option] = None
        return dict1