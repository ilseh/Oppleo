
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

    INI_MODBUS_INTERVAL = 'MODBUS_INTERVAL'

    INI_AUTO_SESSION_ENABLED = 'AUTO_SESSION_ENABLED'
    INI_AUTO_SESSION_MINUTES = 'AUTO_SESSION_MINUTES'
    INI_AUTO_SESSION_ENERGY = 'AUTO_SESSION_ENERGY'
    INI_AUTO_SESSION_CONDENSE_SAME_ODOMETER = 'AUTO_SESSION_CONDENSE_SAME_ODOMETER'

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

    # Number of seconds between consecutive kwh meter readouts (via modbus). Only changes will be stored in the 
    # usage table. Greater values will lead to lagging change detection. Smaller values take more processing.
    modbusInterval = 10

    # Auto Session starts a new session when the EVSE starts charging and during the set amount of minutes less
    # than the amount of energy has been consumed (auto was away)
    # A Tesla Model 3 75kWh Dual Motor charges 0.2kWh every 1:23h (16 feb 2020)
    autoSessionEnabled = False
    autoSessionMinutes = 90
    autoSessionEnergy = 0.1
    # Condenses autyo-generated sessions (after a period of inactivity) if the odometer has not changed.
    # Auto-sessions can be generated after the charger was switched off in peak period. Start of off-peak then leads to 
    # an incorrectly auto-generated charge-session, while the vehicke actually has not moved.
    # This does not condense sessions stopped and started through RFID or WebApp.
    autoSessionCondenseSameOdometer = False

    sqlalchemy_engine = None
    sqlalchemy_session_factory = None
    sqlalchemy_session = None

    # WebAppConfig Logger
    logger = None
    PROCESS_NAME = 'PythonProc'
    LOG_FILE = '/tmp/%s.log' % PROCESS_NAME

    # The time between database queries for energy state updates
    device_measurement_check_interval = 7

    meuThread = None
    chThread = None


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
        print('Configuration loaded')

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
                WebAppConfig.httpPort = WebAppConfig.getIntOption(targetSectionName, WebAppConfig.INI_HTTP_PORT, WebAppConfig.httpPort)
                WebAppConfig.useReloader = WebAppConfig.getBooleanOption(targetSectionName, WebAppConfig.INI_USE_RELOADER, WebAppConfig.useReloader)

                WebAppConfig.factor_Whkm = WebAppConfig.getFloatOption(targetSectionName, WebAppConfig.INI_FACTOR_WHKM, WebAppConfig.factor_Whkm)

                WebAppConfig.modbusInterval = WebAppConfig.getIntOption(targetSectionName, WebAppConfig.INI_MODBUS_INTERVAL, WebAppConfig.modbusInterval)

                WebAppConfig.autoSessionEnabled = WebAppConfig.getBooleanOption(targetSectionName, WebAppConfig.INI_AUTO_SESSION_ENABLED, WebAppConfig.autoSessionEnabled)
                WebAppConfig.autoSessionMinutes = WebAppConfig.getIntOption(targetSectionName, WebAppConfig.INI_AUTO_SESSION_MINUTES, WebAppConfig.autoSessionMinutes)
                WebAppConfig.autoSessionEnergy = WebAppConfig.getFloatOption(targetSectionName, WebAppConfig.INI_AUTO_SESSION_ENERGY, WebAppConfig.autoSessionEnergy)
                WebAppConfig.autoSessionCondenseSameOdometer = WebAppConfig.getBooleanOption(targetSectionName, WebAppConfig.INI_AUTO_SESSION_CONDENSE_SAME_ODOMETER, WebAppConfig.autoSessionCondenseSameOdometer)

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
        WebAppConfig.LOG_FILE = '/tmp/%s.log' % WebAppConfig.PROCESS_NAME
#        WebAppConfig.LOG_FILE = '/home/pi/%s.log' % WebAppConfig.PROCESS_NAME
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

    @staticmethod
    def sqlAlchemyPoolStatus() -> dict:
        WebAppConfig.logger.debug('sqlAlchemyPoolStatus()')
        if WebAppConfig.sqlalchemy_engine is None or \
           WebAppConfig.sqlalchemy_engine.pool is None:
            WebAppConfig.logger.warning('sqlAlchemyPoolStatus() - no engine or pool (None)')
            return "Geen informatie"
        else:
            pool_status = WebAppConfig.sqlalchemy_engine.pool.status()
            WebAppConfig.logger.info('sqlAlchemyPoolStatus() - %s' % pool_status)
            return pool_status
