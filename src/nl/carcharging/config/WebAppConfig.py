import os
from nl.carcharging.config import Logger
import logging

class Config(object):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')

class Development(Config):
    """
    Development environment configuration
    """
    DEBUG = True
    TESTING = False

class Production(Config):
    """
    Production environment configurations
    """
    DEBUG = False
    TESTING = False

# Global variable does work in werkzeug but not un uWSGI
# Therefore added as static to WebAppConfig Class
app_config = {
    'development': Development,
    'production': Production,
}

# 
class WebAppConfig(object):
    login_manager = None
    socketio = None

    PARAM_ENV = 'CARCHARGING_ENV'
    PARAM_DB_URL = 'DATABASE_URL'
    env = {
        'development': Development,
        'production': Production,
    }
    sqlalchemy_engine = None
    sqlalchemy_session_factory = None
    sqlalchemy_session = None
    PROCESS_NAME = 'PythonProc'
    LOG_FILE = '/tmp/%s.log' % PROCESS_NAME

    @staticmethod
    def initLogger(process_name='PythonProc'):
        WebAppConfig.PROCESS_NAME = process_name
        WebAppConfig.LOG_FILE = '/tmp/%s.log' % WebAppConfig.PROCESS_NAME
        Logger.init_log(WebAppConfig.PROCESS_NAME, WebAppConfig.LOG_FILE)