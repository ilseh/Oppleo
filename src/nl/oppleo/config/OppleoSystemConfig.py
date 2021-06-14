
from configparser import ConfigParser, NoSectionError, NoOptionError, ExtendedInterpolation
import logging
import os

from base64 import b64encode
from werkzeug.security import generate_password_hash, check_password_hash
from nl.oppleo.config import Logger
from nl.oppleo.utils.WebSocketUtil import WebSocketUtil


"""
 First init the Logger, then load the config
"""

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class OppleoSystemConfig(object, metaclass=Singleton):
    """
        Private variables
    """
    __logger = None
    __ini_settings = None
    __restartRequired = False

    """ Libraries installed """
    __mfrc522 = False
    __rpigpio = False

    """
        Ini file parameter keys
    """
    __INI_MAIN = 'Oppleo'
    __PROCESS_NAME = __INI_MAIN

    # Params are all read as lowercase by ConfigParser (!)
    __INI_SIGNATURE = 'SIGNATURE'
    __INI_LOG_FILE = 'LOG_FILE'

    __INI_LOG_LEVEL = 'LOG_LEVEL'
    __INI_LOG_MAX_BYTES = 'LOG_MAX_FILESIZE'
    __INI_LOG_BACKUP_COUNT = 'LOG_FILE_BACKUP_COUNT'

    __INI_DATABASE_URL = 'DATABASE_URL'
    __INI_SQLALCHEMY_TRACK_MODIFICATIONS = 'SQLALCHEMY_TRACK_MODIFICATIONS'

    ''' The Enable/Disable EVSE GPIO output '''
    __INI_EVSE_SWITCH = 'EVSE_SWITCH'
    ''' The EVSE Status LED blink interpreter via GPIO '''
    __INI_EVSE_LED_READER = 'EVSE_LED_READER'
    ''' The Buzzer GPIO output '''
    __INI_BUZZER = 'BUZZER'
    ''' The Oppleo status LED GPIO output '''
    __INI_OPPLEO_LED = 'OPPLEO_LED'
    ''' The MFRC522 Rfid Reader on SPI via GPIO output '''
    __INI_RFID = 'MFRC522_RFID_READER'

    __INI_HTTP_HOST = 'http_host'
    __INI_HTTP_PORT = 'http_port'
    __INI_HTTP_TIMEOUT = 'http_timeout'
    __INI_DEBUG = 'DEBUG'

    __INI_PYTHONPATH = 'PYTHONPATH'
    __INI_EXPLAIN_TEMPLATE_LOADING = 'EXPLAIN_TEMPLATE_LOADING'

    __INI_MAGIC_PASSWORD = 'MAGIC_PASSWORD'

    __INI_ON_DB_FAILURE_ALLOW_RESTART = 'on_db_failure_allow_restart'
    __INI_ON_DB_FAILURE_MAGIC_PASSWORD = 'on_db_failure_magic_password'
    __INI_ON_DB_FAILURE_ALLOW_URL_CHANGE = 'on_db_failure_allow_url_change'
    __INI_ON_DB_FAILURE_SHOW_CURRENT_URL = 'on_db_failure_show_current_url'

    __INI_PROWL_ENABLED = 'prowl_enabled'
    __INI_PROWL_API_KEY = 'prowl_api_key'

    """
        Variables stored in the INI file 
    """
    __SIGNATURE = b64encode(os.urandom(24)).decode('utf-8')

    __DATABASE_URL = 'postgresql://username:password@localhost:5432/database'
    __SQLALCHEMY_TRACK_MODIFICATIONS = True

    __LOG_FILE = '/tmp/%s.log' % __PROCESS_NAME
    __LOG_LEVEL_STR = 'warning'
    __LOG_MAX_BYTES = 524288
    __LOG_BACKUP_COUNT = 5

    ''' The Enable/Disable EVSE GPIO output '''
    __EVSE_SWITCH_ENABLED = False
    ''' The EVSE Status LED blink interpreter via GPIO '''
    __EVSE_LED_READER_ENABLED = False
    ''' The Buzzer GPIO output '''
    __BUZZER_ENABLED = False
    ''' The Oppleo status LED GPIO output '''
    __OPPLEO_LED_ENABLED = False
    ''' The MFRC522 Rfid Reader on SPI via GPIO output '''
    __RFID_ENABLED = False

    __HTTP_HOST = '0.0.0.0'
    __HTTP_PORT = 80
    __HTTP_TIMEOUT = 5
    __DEBUG = True

    __PYTHONPATH = ''
    __EXPLAIN_TEMPLATE_LOADING = False

    __MAGIC_PASSWORD = 'admin'

    __ON_DB_FAILURE_ALLOW_RESTART = False
    __ON_DB_FAILURE_MAGIC_PASSWORD = 'pbkdf2:sha256:150000$vK2k1sfM$e2a41cdd7546cd514304611d018a79753011d4db8b13a6292a7e6bce50cba992'
    __ON_DB_FAILURE_ALLOW_URL_CHANGE = False
    __ON_DB_FAILURE_SHOW_CURRENT_URL = False

    __PROWL_ENABLED = False
    __PROWL_API_KEY = None

    __dbAvailable = False

    """
        Application wide global variables or handles which can be picked op from here
    """
    load_completed = False

    sqlalchemy_engine = None
    sqlalchemy_session_factory = None
    sqlalchemy_session = None
    
    # Copied from oppleoConfig
    wsEmitQueue = None
    chargerName = None

    def __init__(self):
        iniFileNotFound = False
        log = None
        try:
            log = self.__loadConfig__()
        except FileNotFoundError as fnfe:
            # System configuration file not found! (Creating with defaults)
            iniFileNotFound = True
            # Only in this situation, set these params
            self.__ON_DB_FAILURE_ALLOW_RESTART = True
            self.__ON_DB_FAILURE_ALLOW_URL_CHANGE = True
            self.__ON_DB_FAILURE_SHOW_CURRENT_URL = True
            self.__writeConfig__()
        # Start logger after ini load to get configured logfile name or use default
        self.__initLogger__()
        if log is not None and len(log) > 0:
            for log_entry in log:
                if log_entry['type'] == 'error':
                    self.__logger.error(log_entry['entry'])
                if log_entry['type'] == 'debug':
                    self.__logger.debug(log_entry['entry'])

        if iniFileNotFound:
            self.__logger.debug('System configuration file not found! (Creating with defaults)')




    """
        returns the absolute path to oppleo.ini
    """
    def __getConfigFile__(self):
        return os.path.join(os.path.dirname(os.path.realpath(__file__)), 'oppleo.ini')


    def __loadConfig__(self):
        log = [] if self.__logger is None else None
        lt = 'Initializing Oppleo System...'
        self.__logger.debug(lt) if self.__logger is not None else log.append({ 'type': 'debug', 'entry': lt })

        # Load the ini file
        if (self.__ini_settings is None):
            self.__ini_settings = ConfigParser()

        # The absolute dir the script is in
        configFile = self.__getConfigFile__()
        lt = 'Looking for system configuration file ' + configFile
        self.__logger.debug(lt) if self.__logger is not None else log.append({ 'type': 'debug', 'entry': lt })
        self.__ini_settings.read_file(open(configFile, "r"))

        # Read the ini file
        if not self.__ini_settings.has_section(self.__INI_MAIN):
            lt = 'System configuration file has no ' + self.__INI_MAIN + ' section.'
            self.__logger.debug(lt) if self.__logger is not None else log.append({ 'type': 'debug', 'entry': lt })
            return

        self.__SIGNATURE = self.__getOption__(section=self.__INI_MAIN, option=self.__INI_SIGNATURE, log=log)

        self.__LOG_FILE = self.__getOption__(section=self.__INI_MAIN, option=self.__INI_LOG_FILE, default=self.__LOG_FILE, log=log)
        self.__LOG_LEVEL_STR = self.__getOption__(section=self.__INI_MAIN, option=self.__INI_LOG_LEVEL, default=self.__LOG_LEVEL_STR, log=log)
        self.__LOG_MAX_BYTES = self.__getIntOption__(section=self.__INI_MAIN, option=self.__INI_LOG_MAX_BYTES, default=self.__LOG_MAX_BYTES, log=log)
        self.__LOG_BACKUP_COUNT = self.__getIntOption__(section=self.__INI_MAIN, option=self.__INI_LOG_BACKUP_COUNT, default=self.__LOG_BACKUP_COUNT, log=log)

        self.__DATABASE_URL = self.__getOption__(section=self.__INI_MAIN, option=self.__INI_DATABASE_URL, log=log)
        self.__SQLALCHEMY_TRACK_MODIFICATIONS = self.__getBooleanOption__(section=self.__INI_MAIN, option=self.__INI_SQLALCHEMY_TRACK_MODIFICATIONS, log=log)

        self.__EVSE_SWITCH_ENABLED = self.__getBooleanOption__(section=self.__INI_MAIN, option=self.__INI_EVSE_SWITCH, default=self.__EVSE_SWITCH_ENABLED, log=log)
        self.__EVSE_LED_READER_ENABLED = self.__getBooleanOption__(section=self.__INI_MAIN, option=self.__INI_EVSE_LED_READER, default=self.__EVSE_LED_READER_ENABLED, log=log)
        self.__BUZZER_ENABLED = self.__getBooleanOption__(section=self.__INI_MAIN, option=self.__INI_BUZZER, default=self.__BUZZER_ENABLED, log=log)
        self.__OPPLEO_LED_ENABLED = self.__getBooleanOption__(section=self.__INI_MAIN, option=self.__INI_OPPLEO_LED, default=self.__OPPLEO_LED_ENABLED, log=log)
        self.__RFID_ENABLED = self.__getBooleanOption__(section=self.__INI_MAIN, option=self.__INI_RFID, default=self.__RFID_ENABLED, log=log)

        self.__HTTP_HOST = self.__getOption__(section=self.__INI_MAIN, option=self.__INI_HTTP_HOST, default=self.__HTTP_HOST, log=log)
        self.__HTTP_PORT = self.__getIntOption__(section=self.__INI_MAIN, option=self.__INI_HTTP_PORT, default=self.__HTTP_PORT, log=log)
        self.__HTTP_TIMEOUT = self.__getIntOption__(section=self.__INI_MAIN, option=self.__INI_HTTP_TIMEOUT, default=self.__HTTP_TIMEOUT, log=log)

        self.__DEBUG = self.__getBooleanOption__(section=self.__INI_MAIN, option=self.__INI_DEBUG, log=log)

        self.__PYTHONPATH = self.__getOption__(section=self.__INI_MAIN, option=self.__INI_PYTHONPATH, log=log)
        self.__EXPLAIN_TEMPLATE_LOADING = self.__getBooleanOption__(section=self.__INI_MAIN, option=self.__INI_EXPLAIN_TEMPLATE_LOADING, log=log)

        self.__ON_DB_FAILURE_ALLOW_RESTART = self.__getBooleanOption__(section=self.__INI_MAIN, option=self.__INI_ON_DB_FAILURE_ALLOW_RESTART, log=log)
        self.__ON_DB_FAILURE_MAGIC_PASSWORD = self.__getOption__(section=self.__INI_MAIN, option=self.__INI_ON_DB_FAILURE_MAGIC_PASSWORD, log=log)
        self.__ON_DB_FAILURE_ALLOW_URL_CHANGE = self.__getBooleanOption__(section=self.__INI_MAIN, option=self.__INI_ON_DB_FAILURE_ALLOW_URL_CHANGE, log=log)
        self.__ON_DB_FAILURE_SHOW_CURRENT_URL = self.__getBooleanOption__(section=self.__INI_MAIN, option=self.__INI_ON_DB_FAILURE_SHOW_CURRENT_URL, log=log)

        self.__PROWL_ENABLED = self.__getBooleanOption__(section=self.__INI_MAIN, option=self.__INI_PROWL_ENABLED, default=self.__PROWL_ENABLED, log=log)
        self.__PROWL_API_KEY = self.__getOption__(section=self.__INI_MAIN, option=self.__INI_PROWL_API_KEY, default=self.__PROWL_API_KEY, log=log)

        self.load_completed = True
        
        lt = 'System configuration loaded'
        self.__logger.debug(lt) if self.__logger is not None else log.append({ 'type': 'debug', 'entry': lt })

        if log is not None and len(log) > 0:
            return log


    def reload(self):
        self.__logger.debug("Reloading...")
        # File should exist, on init it is created if it didn't exist
        self.__loadConfig__()


    def __writeConfig__(self):
        self.__logger.debug('Writing the Oppleo System settings...')
        if (self.__ini_settings is None):
            self.__ini_settings = ConfigParser()

        # Try to add the main section
        try:
            self.__ini_settings.add_section(self.__INI_MAIN)
        except:
            # DuplicateSectionError - Section already exists
            # ValueError - Default Section
            # TypeError - Section name not a string
            pass
        try:
            # Set the parameters
            self.__ini_settings[self.__INI_MAIN][self.__INI_SIGNATURE] = self.__SIGNATURE

            self.__ini_settings[self.__INI_MAIN][self.__INI_LOG_FILE] = self.__LOG_FILE
            self.__ini_settings[self.__INI_MAIN][self.__INI_LOG_LEVEL] = self.__LOG_LEVEL_STR
            self.__ini_settings[self.__INI_MAIN][self.__INI_LOG_MAX_BYTES] = str(self.__LOG_MAX_BYTES)
            self.__ini_settings[self.__INI_MAIN][self.__INI_LOG_BACKUP_COUNT] = str(self.__LOG_BACKUP_COUNT)

            self.__ini_settings[self.__INI_MAIN][self.__INI_DATABASE_URL] = self.__DATABASE_URL
            self.__ini_settings[self.__INI_MAIN][self.__INI_SQLALCHEMY_TRACK_MODIFICATIONS] = 'True' if self.__SQLALCHEMY_TRACK_MODIFICATIONS else 'False'

            self.__ini_settings[self.__INI_MAIN][self.__INI_EVSE_SWITCH] = 'True' if self.__EVSE_SWITCH_ENABLED else 'False'
            self.__ini_settings[self.__INI_MAIN][self.__INI_EVSE_LED_READER] = 'True' if self.__EVSE_LED_READER_ENABLED else 'False'
            self.__ini_settings[self.__INI_MAIN][self.__INI_BUZZER] = 'True' if self.__BUZZER_ENABLED else 'False'
            self.__ini_settings[self.__INI_MAIN][self.__INI_OPPLEO_LED] = 'True' if self.__OPPLEO_LED_ENABLED else 'False'
            self.__ini_settings[self.__INI_MAIN][self.__INI_RFID] = 'True' if self.__RFID_ENABLED else 'False'

            self.__ini_settings[self.__INI_MAIN][self.__INI_HTTP_HOST] = self.__HTTP_HOST
            self.__ini_settings[self.__INI_MAIN][self.__INI_HTTP_PORT] = str(self.__HTTP_PORT)
            self.__ini_settings[self.__INI_MAIN][self.__INI_HTTP_TIMEOUT] = str(self.__HTTP_TIMEOUT)

            self.__ini_settings[self.__INI_MAIN][self.__INI_DEBUG] = 'True' if self.__DEBUG else 'False'

            self.__ini_settings[self.__INI_MAIN][self.__INI_PYTHONPATH] = self.__PYTHONPATH
            self.__ini_settings[self.__INI_MAIN][self.__INI_EXPLAIN_TEMPLATE_LOADING] = 'True' if self.__EXPLAIN_TEMPLATE_LOADING else 'False'

            self.__ini_settings[self.__INI_MAIN][self.__INI_ON_DB_FAILURE_ALLOW_RESTART] = 'True' if self.__ON_DB_FAILURE_ALLOW_RESTART else 'False'
            self.__ini_settings[self.__INI_MAIN][self.__INI_ON_DB_FAILURE_MAGIC_PASSWORD] = self.__ON_DB_FAILURE_MAGIC_PASSWORD
            self.__ini_settings[self.__INI_MAIN][self.__INI_ON_DB_FAILURE_ALLOW_URL_CHANGE] = 'True' if self.__ON_DB_FAILURE_ALLOW_URL_CHANGE else 'False'
            self.__ini_settings[self.__INI_MAIN][self.__INI_ON_DB_FAILURE_SHOW_CURRENT_URL] = 'True' if self.__ON_DB_FAILURE_SHOW_CURRENT_URL else 'False'

            self.__ini_settings[self.__INI_MAIN][self.__INI_PROWL_ENABLED] = 'True' if self.__PROWL_ENABLED else 'False'
            if self.__PROWL_API_KEY is not None:
                self.__ini_settings[self.__INI_MAIN][self.__INI_PROWL_API_KEY] = self.__PROWL_API_KEY

            # Write actial file
            with open(self.__getConfigFile__(), 'w') as configfile:
                self.__ini_settings.write(configfile)
        except Exception as e:
            pass


    def __getBooleanOption__(self, section, option, default=False, log:list=None):
        if not self.__ini_settings.has_option(section, option):
            if log is not None:
                log.append({ 'type': 'error', 'entry': 'Ini file ERROR: No ' + option + ' in ' + section })
            if self.__logger is not None:
                self.__logger.error('Ini file ERROR: No ' + option + ' in ' + section)
            return default
        return self.__ini_settings.getboolean(section, option)

    def __getIntOption__(self, section, option, default=0, log:list=None):
        if not self.__ini_settings.has_option(section, option):
            if log is not None:
                log.append({ 'type': 'error', 'entry': 'Ini file ERROR: No ' + option + ' in ' + section })
            if self.__logger is not None:
                self.__logger.error('Ini file ERROR: No ' + option + ' in ' + section)
            return default
        return self.__ini_settings.getint(section, option)

    def __getFloatOption__(self, section, option, default=0, log:list=None):
        if not self.__ini_settings.has_option(section, option):
            if log is not None:
                log.append({ 'type': 'error', 'entry': 'Ini file ERROR: No ' + option + ' in ' + section })
            if self.__logger is not None:
                self.__logger.error('Ini file ERROR: No ' + option + ' in ' + section)
            return default
        return self.__ini_settings.getfloat(section, option)

    def __getOption__(self, section, option, default='', log:list=None):
        if not self.__ini_settings.has_option(section, option):
            if log is not None:
                log.append({ 'type': 'error', 'entry': 'Ini file ERROR: No ' + option + ' in ' + section })
            if self.__logger is not None:
                self.__logger.error('Ini file ERROR: No ' + option + ' in ' + section)
            return default
        return self.__ini_settings.get(section, option)

    def __configSectionMap__(self, section):
        dict1 = {}
        try:
            options = self.__ini_settings.options(section)
        except NoSectionError:
            self.__logger.error('Ini file Section: %s not found in ini file' % section)
            return

        for option in options:
            try:
                dict1[option] = self.__ini_settings.get(section, option)
                if dict1[option] == -1:
                    self.__logger.debug('Ini file excskip %s' % option)
            except NoOptionError:
                self.__logger.error('Ini file exception on %s!' % option)
                dict1[option] = None
        return dict1


    def __initLogger__(self):
        Logger.init_log(process_name=self.__PROCESS_NAME,
                        log_file=self.__LOG_FILE,
                        loglevel=self.intoLogLevel(self.__LOG_LEVEL_STR),
                        maxBytes=self.__LOG_MAX_BYTES,
                        backupCount=self.__LOG_BACKUP_COUNT
                        )
        self.__logger = logging.getLogger('nl.oppleo.config.OppleoSystemConfig')


    def sqlAlchemyPoolStatus(self) -> dict:
        self.__logger.debug('sqlAlchemyPoolStatus()')
        if self.sqlalchemy_engine is None or \
           self.sqlalchemy_engine.pool is None:
            self.__logger.warning('sqlAlchemyPoolStatus() - no engine or pool (None)')
            return {}
        else:
            pool_status = self.sqlalchemy_engine.pool.status()
            self.__logger.info('sqlAlchemyPoolStatus() - {}'.format(pool_status))
            return pool_status

    """
        SIGNATURE
    """
    @property
    def SIGNATURE(self):
        return self.__SIGNATURE

    @SIGNATURE.setter
    def SIGNATURE(self, value):
        raise ValueError('SIGNATURE cannot be set')


    """
        DATABASE_URL
    """
    @property
    def DATABASE_URL(self):
        return self.__DATABASE_URL

    @DATABASE_URL.setter
    def DATABASE_URL(self, value):
        self.__DATABASE_URL = value
        self.__writeConfig__()
        self.restartRequired = True

    """
        SQLALCHEMY_TRACK_MODIFICATIONS
    """
    @property
    def SQLALCHEMY_TRACK_MODIFICATIONS(self):
        return bool(self.__SQLALCHEMY_TRACK_MODIFICATIONS)

    @SQLALCHEMY_TRACK_MODIFICATIONS.setter
    def SQLALCHEMY_TRACK_MODIFICATIONS(self, value):
        self.__SQLALCHEMY_TRACK_MODIFICATIONS = value
        self.__writeConfig__()
        self.restartRequired = True

    """
        PROCESS_NAME
    """
    @property
    def PROCESS_NAME(self):
        return self.__PROCESS_NAME

    @PROCESS_NAME.setter
    def PROCESS_NAME(self, value):
        raise NotImplementedError('PROCESS_NAME set in code.')

    """
        logFile -> LOG_FILE
    """
    @property
    def logFile(self):
        return self.__LOG_FILE

    @logFile.setter
    def logFile(self, value):
        self.__LOG_FILE = value
        self.__writeConfig__()
        self.restartRequired = True

    """
        evseSwitchEnabled
        The Enable/Disable EVSE GPIO output
    """
    @property
    def evseSwitchEnabled(self):
        return self.__EVSE_SWITCH_ENABLED

    @evseSwitchEnabled.setter
    def evseSwitchEnabled(self, value):
        self.__EVSE_SWITCH_ENABLED = value
        self.__writeConfig__()
        self.restartRequired = True

    """
        evseLedReaderEnabled
        The EVSE Status LED blink interpreter via GPIO
    """
    @property
    def evseLedReaderEnabled(self):
        return self.__EVSE_LED_READER_ENABLED

    @evseLedReaderEnabled.setter
    def evseLedReaderEnabled(self, value):
        self.__EVSE_LED_READER_ENABLED = value
        self.__writeConfig__()
        self.restartRequired = True

    """
        buzzerEnabled
        The Buzzer GPIO output
    """
    @property
    def buzzerEnabled(self):
        return self.__BUZZER_ENABLED

    @buzzerEnabled.setter
    def buzzerEnabled(self, value):
        self.__BUZZER_ENABLED = value
        self.__writeConfig__()
        self.restartRequired = True

    """
        oppleoLedEnabled
        The Oppleo status LED GPIO output
        - if this is moved to the database and OppleoConfig, resetting the RGBLedControllerThread becomes possible.
    """
    @property
    def oppleoLedEnabled(self):
        return self.__OPPLEO_LED_ENABLED

    @oppleoLedEnabled.setter
    def oppleoLedEnabled(self, value):
        self.__OPPLEO_LED_ENABLED = value
        self.__writeConfig__()
        self.restartRequired = True

    """
        rfidEnabled
        The MFRC522 Rfid Reader on SPI via GPIO output
    """
    @property
    def rfidEnabled(self):
        return self.__RFID_ENABLED

    @rfidEnabled.setter
    def rfidEnabled(self, value):
        self.__RFID_ENABLED = value
        self.__writeConfig__()
        # No restart required if module is present

    """
        httpHost -> __HTTP_HOST
    """
    @property
    def httpHost(self):
        return self.__HTTP_HOST

    @httpHost.setter
    def httpHost(self, value:str):
        self.__HTTP_HOST = value
        self.__writeConfig__()
        self.restartRequired = True

    """
        httpPort -> __HTTP_PORT
    """
    @property
    def httpPort(self):
        return self.__HTTP_PORT

    @httpPort.setter
    def httpPort(self, value:int):
        self.__HTTP_PORT = value
        self.__writeConfig__()
        self.restartRequired = True

    """
        httpTimeout -> __HTTP_TIMEOUT
    """
    @property
    def httpTimeout(self):
        return self.__HTTP_TIMEOUT

    @httpTimeout.setter
    def httpTimeout(self, value:int):
        self.__HTTP_TIMEOUT = value
        self.__writeConfig__()


    """
        DEBUG
    """
    @property
    def DEBUG(self):
        return self.__DEBUG

    @DEBUG.setter
    def DEBUG(self, value):
        self.__DEBUG = value
        self.__writeConfig__()
        self.restartRequired = True

    """
        PYTHONPATH
    """
    @property
    def PYTHONPATH(self):
        return self.__PYTHONPATH

    @PYTHONPATH.setter
    def PYTHONPATH(self, value):
        self.__PYTHONPATH = value
        self.__writeConfig__()
        self.restartRequired = True

    """
        EXPLAIN_TEMPLATE_LOADING
    """
    @property
    def EXPLAIN_TEMPLATE_LOADING(self):
        return self.__EXPLAIN_TEMPLATE_LOADING

    @EXPLAIN_TEMPLATE_LOADING.setter
    def EXPLAIN_TEMPLATE_LOADING(self, value):
        self.__EXPLAIN_TEMPLATE_LOADING = value
        self.__writeConfig__()
        self.restartRequired = True

    """
        dbAvailable
    """
    @property
    def dbAvailable(self):
        return self.__dbAvailable

    @dbAvailable.setter
    def dbAvailable(self, value):
        self.__dbAvailable = value
        self.restartRequired = self.restartRequired or (not value)

    """
        restartRequired (no database persistence)
    """
    @property
    def restartRequired(self):
        return self.__restartRequired

    @restartRequired.setter
    def restartRequired(self, value):
        try: 
            self.__restartRequired = bool(value)
            if (bool(value) and self.wsEmitQueue is not None and self.chargerName is not None):
                # Announce
                WebSocketUtil.emit(
                        wsEmitQueue=self.wsEmitQueue,
                        event='update', 
                        id=self.chargerName,
                        data={
                            "restartRequired"   : self.__restartRequired
#                            "restartRequired"   : self.__restartRequired,
#                            "upSince"           : self.upSinceDatetimeStr,
#                            "clientsConnected"  : len(self.connectedClients)
                        },
                        namespace='/system_status',
                        public=False
                    )

        except ValueError:
            self.__logger.warning("Value {} could not be interpreted as bool".format(value), exc_info=True)


    """
        onDbFailureAllowUrlChange -> __ON_DB_FAILURE_ALLOW_URL_CHANGE
    """
    @property
    def onDbFailureAllowUrlChange(self):
        return self.__ON_DB_FAILURE_ALLOW_URL_CHANGE

    @onDbFailureAllowUrlChange.setter
    def onDbFailureAllowUrlChange(self, value):
        self.__ON_DB_FAILURE_ALLOW_URL_CHANGE = value
        self.__writeConfig__()

    """
        onDbFailureShowCurrentUrl -> __ON_DB_FAILURE_SHOW_CURRENT_URL
    """
    @property
    def onDbFailureShowCurrentUrl(self):
        return self.__ON_DB_FAILURE_SHOW_CURRENT_URL

    @onDbFailureShowCurrentUrl.setter
    def onDbFailureShowCurrentUrl(self, value):
        self.__ON_DB_FAILURE_SHOW_CURRENT_URL = value
        self.__writeConfig__()

    """
        onDbFailureAllowRestart -> __ON_DB_FAILURE_ALLOW_RESTART
    """
    @property
    def onDbFailureAllowRestart(self):
        return self.__ON_DB_FAILURE_ALLOW_RESTART

    @onDbFailureAllowRestart.setter
    def onDbFailureAllowRestart(self, value):
        self.__ON_DB_FAILURE_ALLOW_RESTART = value
        self.__writeConfig__()

    """
        onDbFailureMagicPassword -> __ON_DB_FAILURE_MAGIC_PASSWORD
    """
    @property
    def onDbFailureMagicPassword(self):
        return self.__ON_DB_FAILURE_MAGIC_PASSWORD

    @onDbFailureMagicPassword.setter
    def onDbFailureMagicPassword(self, value):
        self.__ON_DB_FAILURE_MAGIC_PASSWORD = generate_password_hash(value)
        self.__writeConfig__()

    def onDbFailureMagicPasswordCheck(self, value) -> bool:
        return check_password_hash(self.onDbFailureMagicPassword, value)

    """
        prowlEnabled -> __PROWL_ENABLED
    """
    @property
    def prowlEnabled(self):
        return self.__PROWL_ENABLED

    @prowlEnabled.setter
    def prowlEnabled(self, value:bool):
        self.__PROWL_ENABLED = value
        self.__writeConfig__()

    """
        prowlApiKey -> __PROWL_API_KEY
    """
    @property
    def prowlApiKey(self):
        return self.__PROWL_API_KEY

    @prowlApiKey.setter
    def prowlApiKey(self, value:str):
        self.__PROWL_API_KEY = value
        self.__writeConfig__()

    """
        logLevel -> __LOG_LEVEL_STR
    """
    @property
    def logLevel(self):
        return self.__LOG_LEVEL_STR

    @logLevel.setter
    def logLevel(self, value:str):
        if value.lower() in self.logLevelOptions:
            self.__LOG_LEVEL_STR = value.lower()
            self.__writeConfig__()
            self.__initLogger__()

    """
        logMaxBytes -> __LOG_MAX_BYTES
    """
    @property
    def logMaxBytes(self):
        return self.__LOG_MAX_BYTES

    @logMaxBytes.setter
    def logMaxBytes(self, value:int):
        self.__LOG_MAX_BYTES = value
        self.__writeConfig__()
        self.__initLogger__()

    """
        logBackupCount -> __LOG_BACKUP_COUNT
    """
    @property
    def logBackupCount(self):
        return self.__LOG_BACKUP_COUNT

    @logBackupCount.setter
    def logBackupCount(self, value:int):
        self.__LOG_BACKUP_COUNT = value
        self.__writeConfig__()
        self.__initLogger__()

    @property
    def logLevelOptions(self) -> list:
        return ['debug', 'info', 'error', 'critical', 'fatal']

    def intoLogLevel(self, level:str=None) -> int:
        if not isinstance(level, str):
            return logging.WARNING
        level = level.lower()
        if level == 'debug':
            return logging.DEBUG
        if level == 'info':
            return logging.INFO
        if level == 'error':
            return logging.ERROR
        if level == 'critical':
            return logging.CRITICAL
        if level == 'fatal':
            return logging.FATAL
        return logging.WARNING

    def intoLogLevelStr(self, level:int=logging.WARNING) -> str:
        if not isinstance(level, int):
            return 'warning'
        if level == logging.DEBUG:
            return 'debug'
        if level == logging.INFO:
            return 'info'
        if level == logging.ERROR:
            return 'error'
        if level == logging.CRITICAL:
            return 'critical'
        if level == logging.FATAL:
            return 'fatal'
        return 'warning'


oppleoSystemConfig = OppleoSystemConfig()