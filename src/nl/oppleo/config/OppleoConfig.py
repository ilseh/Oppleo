
from configparser import ConfigParser, NoSectionError, NoOptionError, ExtendedInterpolation
import logging
import os
from nl.oppleo.config import Logger

"""
 First init the Logger, then load the config
"""

# 
class OppleoConfig(object):
    # ini file param names
    INI_MAIN = 'Oppleo'
    # Params are all read as lowercase by ConfigParser (!)
    INI_TARGET_PARAM = 'activeTarget'
    INI_ENV_PARAM = 'oppleoEnv'

    INI_DATABASE_URL = 'DATABASE_URL'
    INI_ENERGY_DEVICE_ID = 'ENERGY_DEVICE_ID'
    INI_PYTHONPATH = 'PYTHONPATH'
    INI_SQLALCHEMY_DATABASE_URI = 'SQLALCHEMY_DATABASE_URI'

    INI_SQLALCHEMY_TRACK_MODIFICATIONS = 'SQLALCHEMY_TRACK_MODIFICATIONS'
    INI_EXPLAIN_TEMPLATE_LOADING = 'EXPLAIN_TEMPLATE_LOADING'
    INI_SECRET_KEY = 'SECRET_KEY'
    INI_WTF_CSRF_SECRET_KEY = 'WTF_CSRF_SECRET_KEY'

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

    # GPIO MODE - BCM or BOARD (BCM is more future proof/ less direct hardware related)
    INI_GPIO_MODE = 'GPIO_MODE'
    # Pulsing LED values
    INI_PULSE_LED_MIN = 'PULSE_LED_MIN'
    INI_PULSE_LED_MAX = 'PULSE_LED_MAX'
    # Raspberry PINs - RGB LEDs
    INI_PIN_LED_RED = 'PIN_LED_RED'
    INI_PIN_LED_GREEN = 'PIN_LED_GREEN'
    INI_PIN_LED_BLUE = 'PIN_LED_BLUE'
    # Raspberry PINs - Buzzer - PIN 16/ GPIO23
    INI_PIN_BUZZER = 'PIN_BUZZER' 

    # Off peak
    INI_PEAK_HOURS_OFF_PEAK_ENABLED = 'PEAK_HOURS_OFF_PEAK_ENABLED'

    # ini content
    ini_settings = None

    # INI params
    DATABASE_URL = None
    ENERGY_DEVICE_ID = 'NONE'
    PYTHONPATH = ''
    SQLALCHEMY_DATABASE_URI = None

    SQLALCHEMY_TRACK_MODIFICATIONS = True
    EXPLAIN_TEMPLATE_LOADING = False
    # Replace the SECRET_KEY and WTF_CSRF_SECRET_KEY with random strings. In Python import os and use os.urandom(24) to generate.
    # If these are not in the ini file, each restart all logins expire.
    SECRET_KEY = os.urandom(24)
    WTF_CSRF_SECRET_KEY = os.urandom(24)

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

    # GPIO MODE - BCM or BOARD (BCM is more future proof/ less direct hardware related)
    #   -1 if GPIO.setmode() is not set
    #   11 if GPIO.setmode(GPIO.BCM) is active
    #   10 if GPIO.setmode(GPIO.BOARD) is active
    # Once you’ve set the mode, you can only change it once you’ve done a GPIO.cleanup(). But you can only do 
    # GPIO.cleanup() once you’ve configured a port. You can’t flick between GPIO modes without first setting up 
    # a port, then cleaning up.
    gpioMode = 'BCM'
    # Pulsing LED values
    pulseLedMin = 3
    pulseLedMax = 98
    # Raspberry PINs - RGB LEDs - PINS GPIO13 (Red), GPIO12 (Green) and GPIO 16 (Blue)
    pinLedRed = 13
    pinLedGreen = 12
    pinLedBlue = 16
    # Raspberry PINs - Buzzer - PIN 16/ GPIO23
    pinBuzzer = 23 
    # Raspberry PINs - Buzzer - PIN 29/ GPIO5
    pinEvseSwitch = 5
    # Raspberry PINs - Buzzer - PIN 31/ GPIO6
    pinEvseLed = 6

    # Peak/ Off Peak enabled. If enabled the EVSE will be disabled during off-peak hours
    peakHoursOffPeakEnabled = True
    # Off Peak disabled for this period (not-persistent)
    peakHoursAllowPeakOnePeriod = False

    # Global location to store all connected clients keyed by request.sid (websocket room)    
    connectedClients = {}


    sqlalchemy_engine = None
    sqlalchemy_session_factory = None
    sqlalchemy_session = None

    # OppleoConfig Logger
    logger = None
    PROCESS_NAME = 'PythonProc'
    LOG_FILE = '/tmp/%s.log' % PROCESS_NAME

    # The time between database queries for energy state updates, in seconds
    device_measurement_check_interval = 7

    prowlEnabled = True
    prowlApiKey = '5df94c19d71b4b456efcb49996406fa62e717a44'

    meuThread = None
    chThread = None
    phmThread = None

    wsEmitQueue = None

    @staticmethod
    def loadConfig(filename='oppleo.ini'):
        if OppleoConfig.logger is None:
            OppleoConfig.initLogger()
        OppleoConfig.logger.debug('Initializing Oppleo...')
        # Load the ini file
        OppleoConfig.ini_settings = ConfigParser()
        # Allow dynamic fields in the config ini file
        OppleoConfig.ini_settings._interpolation = ExtendedInterpolation()
        #OppleoConfig.ini_settings.read(filename)
        try:
            # The absolute dir the script is in
            configFile = os.path.join(os.path.dirname(os.path.realpath(__file__)), filename)
            OppleoConfig.logger.debug('Looking for ini file ' + configFile)
            print('Looking for ini file ' + configFile)
            OppleoConfig.ini_settings.read_file(open(configFile, "r"))
        except FileNotFoundError:
            OppleoConfig.logger.debug('Ini file not found!!!')
            print('Ini file not found!!!')
            os._exit(-1)
            return
        print('Configuration loaded')

        # Read the ini file
        if not OppleoConfig.ini_settings.has_section(OppleoConfig.INI_MAIN):
            OppleoConfig.logger.debug('Ini file has no ' + OppleoConfig.INI_MAIN + ' section.')
            return

        mainSectionDict = OppleoConfig.configSectionMap(OppleoConfig.INI_MAIN)
        if mainSectionDict is None:
            return

        # Which target is active?
        if not OppleoConfig.ini_settings.has_option(OppleoConfig.INI_MAIN, OppleoConfig.INI_TARGET_PARAM):
            OppleoConfig.logger.error('Ini file ERROR: No ' + OppleoConfig.INI_TARGET_PARAM + ' in ' + OppleoConfig.INI_MAIN)
        else:
            targetSectionName = OppleoConfig.getOption(OppleoConfig.INI_MAIN, OppleoConfig.INI_TARGET_PARAM)
            if not OppleoConfig.ini_settings.has_section(targetSectionName):
                OppleoConfig.logger.debug('Ini file has no ' + targetSectionName + ' section.')
            else:
                OppleoConfig.DATABASE_URL = OppleoConfig.getOption(targetSectionName, OppleoConfig.INI_DATABASE_URL)
                OppleoConfig.ENERGY_DEVICE_ID = OppleoConfig.getOption(targetSectionName, OppleoConfig.INI_ENERGY_DEVICE_ID)
                OppleoConfig.PYTHONPATH = OppleoConfig.getOption(targetSectionName, OppleoConfig.INI_PYTHONPATH)
                OppleoConfig.SQLALCHEMY_DATABASE_URI = OppleoConfig.getOption(targetSectionName, OppleoConfig.INI_SQLALCHEMY_DATABASE_URI)

                OppleoConfig.SQLALCHEMY_TRACK_MODIFICATIONS = OppleoConfig.getBooleanOption(targetSectionName, OppleoConfig.INI_SQLALCHEMY_TRACK_MODIFICATIONS)
                OppleoConfig.EXPLAIN_TEMPLATE_LOADING = OppleoConfig.getBooleanOption(targetSectionName, OppleoConfig.INI_EXPLAIN_TEMPLATE_LOADING)
                OppleoConfig.SECRET_KEY = OppleoConfig.getOption(targetSectionName, OppleoConfig.INI_SECRET_KEY)
                OppleoConfig.WTF_CSRF_SECRET_KEY = OppleoConfig.getOption(targetSectionName, OppleoConfig.INI_WTF_CSRF_SECRET_KEY)

                OppleoConfig.httpHost = OppleoConfig.getOption(targetSectionName, OppleoConfig.INI_HTTP_HOST)
                OppleoConfig.httpPort = OppleoConfig.getIntOption(targetSectionName, OppleoConfig.INI_HTTP_PORT, OppleoConfig.httpPort)
                OppleoConfig.useReloader = OppleoConfig.getBooleanOption(targetSectionName, OppleoConfig.INI_USE_RELOADER, OppleoConfig.useReloader)

                OppleoConfig.factor_Whkm = OppleoConfig.getFloatOption(targetSectionName, OppleoConfig.INI_FACTOR_WHKM, OppleoConfig.factor_Whkm)

                OppleoConfig.modbusInterval = OppleoConfig.getIntOption(targetSectionName, OppleoConfig.INI_MODBUS_INTERVAL, OppleoConfig.modbusInterval)

                OppleoConfig.autoSessionEnabled = OppleoConfig.getBooleanOption(targetSectionName, OppleoConfig.INI_AUTO_SESSION_ENABLED, OppleoConfig.autoSessionEnabled)
                OppleoConfig.autoSessionMinutes = OppleoConfig.getIntOption(targetSectionName, OppleoConfig.INI_AUTO_SESSION_MINUTES, OppleoConfig.autoSessionMinutes)
                OppleoConfig.autoSessionEnergy = OppleoConfig.getFloatOption(targetSectionName, OppleoConfig.INI_AUTO_SESSION_ENERGY, OppleoConfig.autoSessionEnergy)
                OppleoConfig.autoSessionCondenseSameOdometer = OppleoConfig.getBooleanOption(targetSectionName, OppleoConfig.INI_AUTO_SESSION_CONDENSE_SAME_ODOMETER, OppleoConfig.autoSessionCondenseSameOdometer)

                OppleoConfig.gpioMode = OppleoConfig.getOption(targetSectionName, OppleoConfig.INI_GPIO_MODE, OppleoConfig.gpioMode)

                OppleoConfig.pulseLedMin = OppleoConfig.getIntOption(targetSectionName, OppleoConfig.INI_PULSE_LED_MIN, OppleoConfig.pulseLedMin)
                OppleoConfig.pulseLedMax = OppleoConfig.getIntOption(targetSectionName, OppleoConfig.INI_PULSE_LED_MAX, OppleoConfig.pulseLedMax)
                OppleoConfig.pinLedRed = OppleoConfig.getIntOption(targetSectionName, OppleoConfig.INI_PIN_LED_RED, OppleoConfig.pinLedRed)
                OppleoConfig.pinLedGreen = OppleoConfig.getIntOption(targetSectionName, OppleoConfig.INI_PIN_LED_GREEN, OppleoConfig.pinLedGreen)
                OppleoConfig.pinLedBlue = OppleoConfig.getIntOption(targetSectionName, OppleoConfig.INI_PIN_LED_BLUE, OppleoConfig.pinLedBlue)

                OppleoConfig.pinBuzzer = OppleoConfig.getIntOption(targetSectionName, OppleoConfig.INI_PIN_BUZZER, OppleoConfig.pinBuzzer)

                OppleoConfig.peakHoursOffPeakEnabled = OppleoConfig.getBooleanOption(targetSectionName, OppleoConfig.INI_PEAK_HOURS_OFF_PEAK_ENABLED, OppleoConfig.peakHoursOffPeakEnabled)

        # Which environment is active?
        mainSectionDict = OppleoConfig.configSectionMap(OppleoConfig.INI_MAIN)
        if not OppleoConfig.ini_settings.has_option(OppleoConfig.INI_MAIN, OppleoConfig.INI_ENV_PARAM):
            OppleoConfig.logger.error('Ini file ERROR: No ' + OppleoConfig.INI_ENV_PARAM + ' in ' + OppleoConfig.INI_MAIN)
        else:
            envSectionName = OppleoConfig.getOption(OppleoConfig.INI_MAIN, OppleoConfig.INI_ENV_PARAM)
            if not OppleoConfig.ini_settings.has_section(envSectionName):
                OppleoConfig.logger.debug('Ini file has no ' + envSectionName + ' section.')
            else:
                OppleoConfig.PRODUCTION = ( envSectionName.lower() == OppleoConfig.INI_IS_PROD.lower() )
                OppleoConfig.DEBUG = OppleoConfig.getBooleanOption(envSectionName, OppleoConfig.INI_DEBUG, False)
                OppleoConfig.TESTING = OppleoConfig.getBooleanOption(envSectionName, OppleoConfig.INI_TESTING, False)


    @staticmethod
    def initLogger(process_name='PythonProc'):
        OppleoConfig.PROCESS_NAME = process_name
        OppleoConfig.LOG_FILE = '/tmp/%s.log' % OppleoConfig.PROCESS_NAME
#        OppleoConfig.LOG_FILE = '/home/pi/%s.log' % OppleoConfig.PROCESS_NAME
        Logger.init_log(OppleoConfig.PROCESS_NAME, OppleoConfig.LOG_FILE)
        OppleoConfig.logger = logging.getLogger('nl.oppleo.webapp.WebApp')


    @staticmethod
    def getBooleanOption(section, option, default=False):
        if not OppleoConfig.ini_settings.has_option(section, option):
            OppleoConfig.logger.error('Ini file ERROR: No ' + option + ' in ' + section)
            return default
        return OppleoConfig.ini_settings.getboolean(section, option)

    @staticmethod
    def getIntOption(section, option, default=0):
        if not OppleoConfig.ini_settings.has_option(section, option):
            OppleoConfig.logger.error('Ini file ERROR: No ' + option + ' in ' + section)
            return default
        return OppleoConfig.ini_settings.getint(section, option)

    @staticmethod
    def getFloatOption(section, option, default=0):
        if not OppleoConfig.ini_settings.has_option(section, option):
            OppleoConfig.logger.error('Ini file ERROR: No ' + option + ' in ' + section)
            return default
        return OppleoConfig.ini_settings.getfloat(section, option)

    @staticmethod
    def getOption(section, option, default=''):
        if not OppleoConfig.ini_settings.has_option(section, option):
            OppleoConfig.logger.error('Ini file ERROR: No ' + option + ' in ' + section)
            return default
        return OppleoConfig.ini_settings.get(section, option)

    @staticmethod
    def configSectionMap(section):
        dict1 = {}
        try:
            options = OppleoConfig.ini_settings.options(section)
        except NoSectionError:
            OppleoConfig.logger.error('Ini file Section: %s not found in ini file' % section)
            return

        for option in options:
            try:
                dict1[option] = OppleoConfig.ini_settings.get(section, option)
                if dict1[option] == -1:
                    OppleoConfig.logger.debug('Ini file excskip %s' % option)
            except NoOptionError:
                OppleoConfig.logger.error('Ini file exception on %s!' % option)
                dict1[option] = None
        return dict1

    @staticmethod
    def sqlAlchemyPoolStatus() -> dict:
        OppleoConfig.logger.debug('sqlAlchemyPoolStatus()')
        if OppleoConfig.sqlalchemy_engine is None or \
           OppleoConfig.sqlalchemy_engine.pool is None:
            OppleoConfig.logger.warning('sqlAlchemyPoolStatus() - no engine or pool (None)')
            return "Geen informatie"
        else:
            pool_status = OppleoConfig.sqlalchemy_engine.pool.status()
            OppleoConfig.logger.info('sqlAlchemyPoolStatus() - %s' % pool_status)
            return pool_status
