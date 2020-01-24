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

