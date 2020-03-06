
from configparser import ConfigParser, NoSectionError, NoOptionError, ExtendedInterpolation
import logging
import os
from nl.oppleo.config import Logger

"""
 First init the Logger, then load the config
"""

# 
class OppleoDatabaseConfig(object):
    logger = None
    ini_settings = None

    # ini file param names
    INI_MAIN = 'OppleoDatabase'
    # Params are all read as lowercase by ConfigParser (!)
    INI_DATABASE_URL = 'DATABASE_URL'
    INI_SQLALCHEMY_DATABASE_URI = 'SQLALCHEMY_DATABASE_URI'
    INI_SQLALCHEMY_TRACK_MODIFICATIONS = 'SQLALCHEMY_TRACK_MODIFICATIONS'

    # INI params
    DATABASE_URL = None
    SQLALCHEMY_DATABASE_URI = None
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    sqlalchemy_engine = None
    sqlalchemy_session_factory = None
    sqlalchemy_session = None

    @staticmethod
    def loadConfig(filename='oppleo.database.ini'):
        if OppleoDatabaseConfig.logger is None:
            OppleoDatabaseConfig.initLogger()
        OppleoDatabaseConfig.logger.debug('Initializing Oppleo Database...')
        # Load the ini file
        OppleoDatabaseConfig.ini_settings = ConfigParser()
        try:
            # The absolute dir the script is in
            configFile = os.path.join(os.path.dirname(os.path.realpath(__file__)), filename)
            OppleoDatabaseConfig.logger.debug('Looking for database configuration file ' + configFile)
            print('Looking for database configuration file ' + configFile)
            OppleoDatabaseConfig.ini_settings.read_file(open(configFile, "r"))
        except FileNotFoundError:
            OppleoDatabaseConfig.logger.debug('Database configuration file not found!!!')
            print('Database configuration file not found!!!')
            os._exit(-1)
            return
        print('Database configuration loaded')

        # Read the ini file
        if not OppleoDatabaseConfig.ini_settings.has_section(OppleoDatabaseConfig.INI_MAIN):
            OppleoDatabaseConfig.logger.debug('Database configuration file has no ' + OppleoDatabaseConfig.INI_MAIN + ' section.')
            return

        OppleoDatabaseConfig.DATABASE_URL = OppleoDatabaseConfig.__getOption(OppleoDatabaseConfig.INI_MAIN, OppleoDatabaseConfig.INI_DATABASE_URL)
        OppleoDatabaseConfig.SQLALCHEMY_DATABASE_URI = OppleoDatabaseConfig.__getOption(OppleoDatabaseConfig.INI_MAIN, OppleoDatabaseConfig.INI_SQLALCHEMY_DATABASE_URI)
        OppleoDatabaseConfig.SQLALCHEMY_TRACK_MODIFICATIONS = OppleoDatabaseConfig.__getBooleanOption(OppleoDatabaseConfig.INI_MAIN, OppleoDatabaseConfig.INI_SQLALCHEMY_TRACK_MODIFICATIONS)


    @staticmethod
    def initLogger():
        OppleoDatabaseConfig.logger = logging.getLogger('nl.oppleo.config.OppleoDatabaseConfig')


    @staticmethod
    def __getBooleanOption(section, option, default=False):
        if not OppleoDatabaseConfig.ini_settings.has_option(section, option):
            OppleoDatabaseConfig.logger.error('Ini file ERROR: No ' + option + ' in ' + section)
            return default
        return OppleoDatabaseConfig.ini_settings.getboolean(section, option)

    @staticmethod
    def __getIntOption(section, option, default=0):
        if not OppleoDatabaseConfig.ini_settings.has_option(section, option):
            OppleoDatabaseConfig.logger.error('Ini file ERROR: No ' + option + ' in ' + section)
            return default
        return OppleoDatabaseConfig.ini_settings.getint(section, option)

    @staticmethod
    def __getFloatOption(section, option, default=0):
        if not OppleoDatabaseConfig.ini_settings.has_option(section, option):
            OppleoDatabaseConfig.logger.error('Ini file ERROR: No ' + option + ' in ' + section)
            return default
        return OppleoDatabaseConfig.ini_settings.getfloat(section, option)

    @staticmethod
    def __getOption(section, option, default=''):
        if not OppleoDatabaseConfig.ini_settings.has_option(section, option):
            OppleoDatabaseConfig.logger.error('Ini file ERROR: No ' + option + ' in ' + section)
            return default
        return OppleoDatabaseConfig.ini_settings.get(section, option)

    @staticmethod
    def __configSectionMap(section):
        dict1 = {}
        try:
            options = OppleoDatabaseConfig.ini_settings.options(section)
        except NoSectionError:
            OppleoDatabaseConfig.logger.error('Ini file Section: %s not found in ini file' % section)
            return

        for option in options:
            try:
                dict1[option] = OppleoDatabaseConfig.ini_settings.get(section, option)
                if dict1[option] == -1:
                    OppleoDatabaseConfig.logger.debug('Ini file excskip %s' % option)
            except NoOptionError:
                OppleoDatabaseConfig.logger.error('Ini file exception on %s!' % option)
                dict1[option] = None
        return dict1

    @staticmethod
    def sqlAlchemyPoolStatus() -> dict:
        OppleoDatabaseConfig.logger.debug('sqlAlchemyPoolStatus()')
        if OppleoDatabaseConfig.sqlalchemy_engine is None or \
           OppleoDatabaseConfig.sqlalchemy_engine.pool is None:
            OppleoDatabaseConfig.logger.warning('sqlAlchemyPoolStatus() - no engine or pool (None)')
            return "Geen informatie"
        else:
            pool_status = OppleoDatabaseConfig.sqlalchemy_engine.pool.status()
            OppleoDatabaseConfig.logger.info('sqlAlchemyPoolStatus() - %s' % pool_status)
            return pool_status