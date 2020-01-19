import os

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

app_config = {
    'development': Development,
    'production': Production,
}



# 
class WebAppConfig(object):
    login_manager = None
    socketio = None