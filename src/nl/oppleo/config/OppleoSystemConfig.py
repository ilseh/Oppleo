
from configparser import ConfigParser, NoSectionError, NoOptionError, ExtendedInterpolation
import logging
import os
from nl.oppleo.config import Logger

"""
 First init the Logger, then load the config
"""


class OppleoSystemConfig(object):
    """
        Private variables
    """
    __logger = None
    __ini_settings = None

    """
        Ini file parameter keys
    """
    __INI_MAIN = 'Oppleo'

    # Params are all read as lowercase by ConfigParser (!)
    __INI_DATABASE_URL = 'DATABASE_URL'
    __INI_SQLALCHEMY_TRACK_MODIFICATIONS = 'SQLALCHEMY_TRACK_MODIFICATIONS'

    __INI_ENV = 'ENV'
    __INI_DEBUG = 'DEBUG'
    __INI_TESTING = 'TESTING'

    __INI_PYTHONPATH = 'PYTHONPATH'
    __INI_EXPLAIN_TEMPLATE_LOADING = 'EXPLAIN_TEMPLATE_LOADING'

    """
        Variables stored in the INI file 
    """
    DATABASE_URL = None
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    PROCESS_NAME = __INI_MAIN
    LOG_FILE = '/tmp/%s.log' % PROCESS_NAME

    ENV = 'Development'
    DEBUG = True
    TESTING = False

    PYTHONPATH = ''
    EXPLAIN_TEMPLATE_LOADING=False

    """
        Application wide global variables or handles which can be picked op from here
    """
    load_completed = False

    sqlalchemy_engine = None
    sqlalchemy_session_factory = None
    sqlalchemy_session = None

    @staticmethod
    def loadConfig(filename='oppleo.ini'):
        if OppleoSystemConfig.__logger is None:
            OppleoSystemConfig.__initLogger__()
        OppleoSystemConfig.__logger.debug('Initializing Oppleo System...')
        # Load the ini file
        OppleoSystemConfig.ini_settings = ConfigParser()
        try:
            # The absolute dir the script is in
            configFile = os.path.join(os.path.dirname(os.path.realpath(__file__)), filename)
            OppleoSystemConfig.__logger.debug('Looking for system configuration file ' + configFile)
            print('Looking for system configuration file ' + configFile)
            OppleoSystemConfig.ini_settings.read_file(open(configFile, "r"))
        except FileNotFoundError:
            OppleoSystemConfig.__logger.debug('System configuration file not found!!!')
            print('System configuration file not found!!!')
            os._exit(-1)
            return
        print('System configuration loaded')

        # Read the ini file
        if not OppleoSystemConfig.ini_settings.has_section(OppleoSystemConfig.__INI_MAIN):
            OppleoSystemConfig.__logger.debug('System configuration file has no ' + OppleoSystemConfig.__INI_MAIN + ' section.')
            return

        OppleoSystemConfig.DATABASE_URL = OppleoSystemConfig.__getOption__(OppleoSystemConfig.__INI_MAIN, OppleoSystemConfig.__INI_DATABASE_URL)
        OppleoSystemConfig.SQLALCHEMY_TRACK_MODIFICATIONS = OppleoSystemConfig.__getBooleanOption__(OppleoSystemConfig.__INI_MAIN, OppleoSystemConfig.__INI_SQLALCHEMY_TRACK_MODIFICATIONS)

        OppleoSystemConfig.ENV = OppleoSystemConfig.__getOption__(OppleoSystemConfig.__INI_MAIN, OppleoSystemConfig.__INI_ENV)
        OppleoSystemConfig.DEBUG = OppleoSystemConfig.__getBooleanOption__(OppleoSystemConfig.__INI_MAIN, OppleoSystemConfig.__INI_DEBUG)
        OppleoSystemConfig.TESTING = OppleoSystemConfig.__getBooleanOption__(OppleoSystemConfig.__INI_MAIN, OppleoSystemConfig.__INI_TESTING)

        OppleoSystemConfig.PYTHONPATH = OppleoSystemConfig.__getOption__(OppleoSystemConfig.__INI_MAIN, OppleoSystemConfig.__INI_PYTHONPATH)
        OppleoSystemConfig.EXPLAIN_TEMPLATE_LOADING = OppleoSystemConfig.__getOption__(OppleoSystemConfig.__INI_MAIN, OppleoSystemConfig.__INI_EXPLAIN_TEMPLATE_LOADING)

        OppleoSystemConfig.load_completed = True


    @staticmethod
    def reload():
        OppleoSystemConfig.__logger.debug("Reloading...")
        OppleoSystemConfig.loadConfig()


    @staticmethod
    def __getBooleanOption__(section, option, default=False):
        if not OppleoSystemConfig.ini_settings.has_option(section, option):
            OppleoSystemConfig.__logger.error('Ini file ERROR: No ' + option + ' in ' + section)
            return default
        return OppleoSystemConfig.ini_settings.getboolean(section, option)

    @staticmethod
    def __getIntOption__(section, option, default=0):
        if not OppleoSystemConfig.ini_settings.has_option(section, option):
            OppleoSystemConfig.__logger.error('Ini file ERROR: No ' + option + ' in ' + section)
            return default
        return OppleoSystemConfig.ini_settings.getint(section, option)

    @staticmethod
    def __getFloatOption__(section, option, default=0):
        if not OppleoSystemConfig.ini_settings.has_option(section, option):
            OppleoSystemConfig.__logger.error('Ini file ERROR: No ' + option + ' in ' + section)
            return default
        return OppleoSystemConfig.ini_settings.getfloat(section, option)

    @staticmethod
    def __getOption__(section, option, default=''):
        if not OppleoSystemConfig.ini_settings.has_option(section, option):
            OppleoSystemConfig.__logger.error('Ini file ERROR: No ' + option + ' in ' + section)
            return default
        return OppleoSystemConfig.ini_settings.get(section, option)

    @staticmethod
    def __configSectionMap__(section):
        dict1 = {}
        try:
            options = OppleoSystemConfig.ini_settings.options(section)
        except NoSectionError:
            OppleoSystemConfig.__logger.error('Ini file Section: %s not found in ini file' % section)
            return

        for option in options:
            try:
                dict1[option] = OppleoSystemConfig.ini_settings.get(section, option)
                if dict1[option] == -1:
                    OppleoSystemConfig.__logger.debug('Ini file excskip %s' % option)
            except NoOptionError:
                OppleoSystemConfig.__logger.error('Ini file exception on %s!' % option)
                dict1[option] = None
        return dict1


    @staticmethod
    def __initLogger__():
        OppleoSystemConfig.LOG_FILE = '/tmp/%s.log' % OppleoSystemConfig.PROCESS_NAME
        Logger.init_log(OppleoSystemConfig.PROCESS_NAME, OppleoSystemConfig.LOG_FILE)
        t = logging.getLogger('nl.oppleo.config.OppleoSystemConfig')
        OppleoSystemConfig.__logger = logging.getLogger('nl.oppleo.config.OppleoSystemConfig')


    @staticmethod
    def sqlAlchemyPoolStatus() -> dict:
        OppleoSystemConfig.__logger.debug('sqlAlchemyPoolStatus()')
        if OppleoSystemConfig.sqlalchemy_engine is None or \
           OppleoSystemConfig.sqlalchemy_engine.pool is None:
            OppleoSystemConfig.__logger.warning('sqlAlchemyPoolStatus() - no engine or pool (None)')
            return "Geen informatie"
        else:
            pool_status = OppleoSystemConfig.sqlalchemy_engine.pool.status()
            OppleoSystemConfig.__logger.info('sqlAlchemyPoolStatus() - %s' % pool_status)
            return pool_status