
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
    INI_HTTP_HOST = 'HTTP_HOST'
    INI_HTTP_PORT = 'HTTP_PORT'
    INI_USE_RELOADER = 'USE_RELOADER'
    INI_FACTOR_WHKM = 'FACTOR_WHKM'

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
    # Flask app
    app = None  
    appSocketIO = None
    httpHost = '0.0.0.0'  
    httpPort = 80
    useReloader = False
    # Factor to calculate km/h equivalent of Wh per km
    # Tesla is using 162, which matches the in-car screen
    # Actual average over first 16.836 km on Tesla Model 3 is 181.8
    factor_Whkm = 162

    sqlalchemy_engine = None
    sqlalchemy_session_factory = None
    sqlalchemy_session = None

    # WebAppConfig Logger
    logger = None
    PROCESS_NAME = 'PythonProc'
    LOG_FILE = '/tmp/%s.log' % PROCESS_NAME

    # The time between database queries for energy state updates
    device_measurement_check_interval = 7

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
            WebAppConfig.logger.debug('Ini file not found!!!')
            print('Ini file not found!!!')
            os._exit(-1)
            return

        # Read the ini file
        if not WebAppConfig.ini_settings.has_section(WebAppConfig.INI_MAIN):
            WebAppConfig.logger.debug('Ini file has no ' + WebAppConfig.INI_MAIN + ' section.')
            return

        mainSectionDict = WebAppConfig.configSectionMap(WebAppConfig.INI_MAIN)
        if mainSectionDict is None:
            return

        # Which target is active?
        if not WebAppConfig.ini_settings.has_option(WebAppConfig.INI_MAIN, WebAppConfig.INI_TARGET_PARAM):
            WebAppConfig.logger.error('Ini file ERROR: No ' + WebAppConfig.INI_TARGET_PARAM + ' in ' + WebAppConfig.INI_MAIN)
        else:
            targetSectionName = WebAppConfig.getOption(WebAppConfig.INI_MAIN, WebAppConfig.INI_TARGET_PARAM)
            if not WebAppConfig.ini_settings.has_section(targetSectionName):
                WebAppConfig.logger.debug('Ini file has no ' + targetSectionName + ' section.')
            else:
                WebAppConfig.DATABASE_URL = WebAppConfig.getOption(targetSectionName, WebAppConfig.INI_DATABASE_URL)
                WebAppConfig.ENERGY_DEVICE_ID = WebAppConfig.getOption(targetSectionName, WebAppConfig.INI_ENERGY_DEVICE_ID)
                WebAppConfig.PYTHONPATH = WebAppConfig.getOption(targetSectionName, WebAppConfig.INI_PYTHONPATH)
                WebAppConfig.SQLALCHEMY_DATABASE_URI = WebAppConfig.getOption(targetSectionName, WebAppConfig.INI_SQLALCHEMY_DATABASE_URI)
                WebAppConfig.httpHost = WebAppConfig.getOption(targetSectionName, WebAppConfig.INI_HTTP_HOST)
                WebAppConfig.httpPort = WebAppConfig.getIntOption(targetSectionName, WebAppConfig.INI_HTTP_PORT, 80)
                WebAppConfig.useReloader = WebAppConfig.getBooleanOption(targetSectionName, WebAppConfig.INI_USE_RELOADER, False)
                WebAppConfig.factor_Whkm = WebAppConfig.getFloatOption(targetSectionName, WebAppConfig.INI_FACTOR_WHKM, 162)

        # Which environment is active?
        mainSectionDict = WebAppConfig.configSectionMap(WebAppConfig.INI_MAIN)
        if not WebAppConfig.ini_settings.has_option(WebAppConfig.INI_MAIN, WebAppConfig.INI_ENV_PARAM):
            WebAppConfig.logger.error('Ini file ERROR: No ' + WebAppConfig.INI_ENV_PARAM + ' in ' + WebAppConfig.INI_MAIN)
        else:
            envSectionName = WebAppConfig.getOption(WebAppConfig.INI_MAIN, WebAppConfig.INI_ENV_PARAM)
            if not WebAppConfig.ini_settings.has_section(envSectionName):
                WebAppConfig.logger.debug('Ini file has no ' + envSectionName + ' section.')
            else:
                WebAppConfig.PRODUCTION = ( envSectionName.lower() == WebAppConfig.INI_IS_PROD.lower() )
                WebAppConfig.DEBUG = WebAppConfig.getBooleanOption(envSectionName, WebAppConfig.INI_DEBUG, False)
                WebAppConfig.TESTING = WebAppConfig.getBooleanOption(envSectionName, WebAppConfig.INI_TESTING, False)


    @staticmethod
    def initLogger(process_name='PythonProc'):
        WebAppConfig.PROCESS_NAME = process_name
#        WebAppConfig.LOG_FILE = '/tmp/%s.log' % WebAppConfig.PROCESS_NAME
        WebAppConfig.LOG_FILE = '/home/pi/%s.log' % WebAppConfig.PROCESS_NAME
        Logger.init_log(WebAppConfig.PROCESS_NAME, WebAppConfig.LOG_FILE)
        WebAppConfig.logger = logging.getLogger('nl.carcharging.webapp.WebApp')


    @staticmethod
    def getBooleanOption(section, option, default=False):
        if not WebAppConfig.ini_settings.has_option(section, option):
            WebAppConfig.logger.error('Ini file ERROR: No ' + option + ' in ' + section)
            return default
        return WebAppConfig.ini_settings.getboolean(section, option)

    @staticmethod
    def getIntOption(section, option, default=0):
        if not WebAppConfig.ini_settings.has_option(section, option):
            WebAppConfig.logger.error('Ini file ERROR: No ' + option + ' in ' + section)
            return default
        return WebAppConfig.ini_settings.getint(section, option)

    @staticmethod
    def getFloatOption(section, option, default=0):
        if not WebAppConfig.ini_settings.has_option(section, option):
            WebAppConfig.logger.error('Ini file ERROR: No ' + option + ' in ' + section)
            return default
        return WebAppConfig.ini_settings.getfloat(section, option)

    @staticmethod
    def getOption(section, option, default=''):
        if not WebAppConfig.ini_settings.has_option(section, option):
            WebAppConfig.logger.error('Ini file ERROR: No ' + option + ' in ' + section)
            return default
        return WebAppConfig.ini_settings.get(section, option)

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