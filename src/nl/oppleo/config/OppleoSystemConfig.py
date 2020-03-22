
from configparser import ConfigParser, NoSectionError, NoOptionError, ExtendedInterpolation
import logging
import os
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

    """
        Ini file parameter keys
    """
    __INI_MAIN = 'Oppleo'
    __PROCESS_NAME = __INI_MAIN

    # Params are all read as lowercase by ConfigParser (!)
    __INI_SIGNATURE = 'SIGNATURE'
    __INI_DATABASE_URL = 'DATABASE_URL'
    __INI_SQLALCHEMY_TRACK_MODIFICATIONS = 'SQLALCHEMY_TRACK_MODIFICATIONS'

    __INI_ENV = 'ENV'
    __INI_DEBUG = 'DEBUG'
    __INI_TESTING = 'TESTING'

    __INI_PYTHONPATH = 'PYTHONPATH'
    __INI_EXPLAIN_TEMPLATE_LOADING = 'EXPLAIN_TEMPLATE_LOADING'

    __INI_MAGIC_PASSWORD = 'MAGIC_PASSWORD'
    __INI_MAGIC_PASSWORD = 'MAGIC_PASSWORD'

    __INI_ON_DB_FAILURE_ALLOW_RESTART = 'on_db_failure_allow_restart'
    __INI_ON_DB_FAILURE_MAGIC_PASSWORD = 'on_db_failure_magic_password'
    __INI_ON_DB_FAILURE_ALLOW_URL_CHANGE = 'on_db_failure_allow_url_change'
    __INI_ON_DB_FAILURE_SHOW_CURRENT_URL = 'on_db_failure_show_current_url'


    """
        Variables stored in the INI file 
    """
    __SIGNATURE = os.urandom(24)
    __DATABASE_URL = 'postgresql://username:password@localhost:5432/database'
    __SQLALCHEMY_TRACK_MODIFICATIONS = True

    __LOG_FILE = '/tmp/%s.log' % __PROCESS_NAME

    __ENV = 'Development'
    __DEBUG = True
    __TESTING = False

    __PYTHONPATH = ''
    __EXPLAIN_TEMPLATE_LOADING = False

    __MAGIC_PASSWORD = 'admin'

    __ON_DB_FAILURE_ALLOW_RESTART = False
    __ON_DB_FAILURE_MAGIC_PASSWORD = 'pbkdf2:sha256:150000$vK2k1sfM$e2a41cdd7546cd514304611d018a79753011d4db8b13a6292a7e6bce50cba992'
    __ON_DB_FAILURE_ALLOW_URL_CHANGE = False
    __ON_DB_FAILURE_SHOW_CURRENT_URL = False

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
        self.__initLogger__()
        try:
            self.__loadConfig__()
        except FileNotFoundError as fnfe:
            self.__logger.debug('System configuration file not found! (Creating with defaults)')
            self.__writeConfig__()


    """
        returns the absolute path to oppleo.ini
    """
    def __getConfigFile__(self):
        return os.path.join(os.path.dirname(os.path.realpath(__file__)), 'oppleo.ini')


    def __loadConfig__(self):
        self.__logger.debug('Initializing Oppleo System...')
        # Load the ini file
        if (self.__ini_settings is None):
            self.__ini_settings = ConfigParser()

        # The absolute dir the script is in
        configFile = self.__getConfigFile__()
        self.__logger.debug('Looking for system configuration file ' + configFile)
        self.__ini_settings.read_file(open(configFile, "r"))

        # Read the ini file
        if not self.__ini_settings.has_section(self.__INI_MAIN):
            self.__logger.debug('System configuration file has no ' + self.__INI_MAIN + ' section.')
            return

        self.__SIGNATURE = self.__getOption__(self.__INI_MAIN, self.__INI_SIGNATURE)

        self.__DATABASE_URL = self.__getOption__(self.__INI_MAIN, self.__INI_DATABASE_URL)
        self.__SQLALCHEMY_TRACK_MODIFICATIONS = self.__getBooleanOption__(self.__INI_MAIN, self.__INI_SQLALCHEMY_TRACK_MODIFICATIONS)

        self.__ENV = self.__getOption__(self.__INI_MAIN, self.__INI_ENV)
        self.__DEBUG = self.__getBooleanOption__(self.__INI_MAIN, self.__INI_DEBUG)
        self.__TESTING = self.__getBooleanOption__(self.__INI_MAIN, self.__INI_TESTING)

        self.__PYTHONPATH = self.__getOption__(self.__INI_MAIN, self.__INI_PYTHONPATH)
        self.__EXPLAIN_TEMPLATE_LOADING = self.__getBooleanOption__(self.__INI_MAIN, self.__INI_EXPLAIN_TEMPLATE_LOADING)

        self.__ON_DB_FAILURE_ALLOW_RESTART = self.__getBooleanOption__(self.__INI_MAIN, self.__INI_ON_DB_FAILURE_ALLOW_RESTART)
        self.__ON_DB_FAILURE_MAGIC_PASSWORD = self.__getOption__(self.__INI_MAIN, self.__INI_ON_DB_FAILURE_MAGIC_PASSWORD)
        self.__ON_DB_FAILURE_ALLOW_URL_CHANGE = self.__getBooleanOption__(self.__INI_MAIN, self.__INI_ON_DB_FAILURE_ALLOW_URL_CHANGE)
        self.__ON_DB_FAILURE_SHOW_CURRENT_URL = self.__getBooleanOption__(self.__INI_MAIN, self.__INI_ON_DB_FAILURE_SHOW_CURRENT_URL)

        self.load_completed = True
        print('System configuration loaded')


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

            self.__ini_settings[self.__INI_MAIN][self.__INI_DATABASE_URL] = self.__DATABASE_URL
            self.__ini_settings[self.__INI_MAIN][self.__INI_SQLALCHEMY_TRACK_MODIFICATIONS] = 'True' if self.__SQLALCHEMY_TRACK_MODIFICATIONS else 'False'

            self.__ini_settings[self.__INI_MAIN][self.__INI_ENV] = self.__ENV
            self.__ini_settings[self.__INI_MAIN][self.__INI_DEBUG] = 'True' if self.__DEBUG else 'False'
            self.__ini_settings[self.__INI_MAIN][self.__INI_TESTING] = 'True' if self.__TESTING else 'False'

            self.__ini_settings[self.__INI_MAIN][self.__INI_PYTHONPATH] = self.__PYTHONPATH
            self.__ini_settings[self.__INI_MAIN][self.__INI_EXPLAIN_TEMPLATE_LOADING] = 'True' if self.__EXPLAIN_TEMPLATE_LOADING else 'False'

            self.__ini_settings[self.__INI_MAIN][self.__INI_ON_DB_FAILURE_ALLOW_RESTART] = 'True' if self.__ON_DB_FAILURE_ALLOW_RESTART else 'False'
            self.__ini_settings[self.__INI_MAIN][self.__INI_ON_DB_FAILURE_MAGIC_PASSWORD] = self.__ON_DB_FAILURE_MAGIC_PASSWORD
            self.__ini_settings[self.__INI_MAIN][self.__INI_ON_DB_FAILURE_ALLOW_URL_CHANGE] = 'True' if self.__ON_DB_FAILURE_ALLOW_URL_CHANGE else 'False'
            self.__ini_settings[self.__INI_MAIN][self.__INI_ON_DB_FAILURE_SHOW_CURRENT_URL] = 'True' if self.__ON_DB_FAILURE_SHOW_CURRENT_URL else 'False'

            # Write actial file
            with open(self.__getConfigFile__(), 'w') as configfile:
                self.__ini_settings.write(configfile)
        except Exception as e:
            pass


    def __getBooleanOption__(self, section, option, default=False):
        if not self.__ini_settings.has_option(section, option):
            self.__logger.error('Ini file ERROR: No ' + option + ' in ' + section)
            return default
        return self.__ini_settings.getboolean(section, option)

    def __getIntOption__(self, section, option, default=0):
        if not self.__ini_settings.has_option(section, option):
            self.__logger.error('Ini file ERROR: No ' + option + ' in ' + section)
            return default
        return self.__ini_settings.getint(section, option)

    def __getFloatOption__(self, section, option, default=0):
        if not self.__ini_settings.has_option(section, option):
            self.__logger.error('Ini file ERROR: No ' + option + ' in ' + section)
            return default
        return self.__ini_settings.getfloat(section, option)

    def __getOption__(self, section, option, default=''):
        if not self.__ini_settings.has_option(section, option):
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
        self.__LOG_FILE = '/tmp/%s.log' % self.__PROCESS_NAME
        Logger.init_log(self.__PROCESS_NAME, self.__LOG_FILE)
        self.__logger = logging.getLogger('nl.oppleo.config.OppleoSystemConfig')


    def sqlAlchemyPoolStatus(self) -> dict:
        self.__logger.debug('sqlAlchemyPoolStatus()')
        if self.sqlalchemy_engine is None or \
           self.sqlalchemy_engine.pool is None:
            self.__logger.warning('sqlAlchemyPoolStatus() - no engine or pool (None)')
            return "Geen informatie"
        else:
            pool_status = self.sqlalchemy_engine.pool.status()
            self.__logger.info('sqlAlchemyPoolStatus() - %s' % pool_status)
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
        LOG_FILE
    """
    @property
    def LOG_FILE(self):
        return self.__LOG_FILE

    @LOG_FILE.setter
    def LOG_FILE(self, value):
        self.__LOG_FILE = value
        self.__writeConfig__()
        self.restartRequired = True

    """
        ENV
    """
    @property
    def ENV(self):
        return self.__ENV

    @ENV.setter
    def ENV(self, value):
        self.__ENV = value
        self.__writeConfig__()
        self.restartRequired = True

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
        TESTING
    """
    @property
    def TESTING(self):
        return self.__TESTING

    @TESTING.setter
    def TESTING(self, value):
        self.__TESTING = value
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
            self.___logger.warning("Value {} could not be interpreted as bool".format(value), exc_info=True)


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
