import os
from nl.oppleo.config import Logger
import logging

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
# Therefore added as static to OppleoConfig Class
app_config = {
    'development': Development,
    'production': Production,
}

