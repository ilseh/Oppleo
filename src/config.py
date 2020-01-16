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
    flask_change_password = None
    password_rules = {
        "uppercase": 1, # required upper case letters.
        "lowercase": 1, # required lower case letters.
        "number_sequence": True, # forbid 3 or more numbers in sequence. ie: 123,234,456 etc.
        "username": True, #  forbid the password from containing the user name (if supplied as user).
        "numbers": 1, #  required numbers.
        "username_length": 0, # minimum length for a username
        "username_requires_separators": False, # username must use . or - inside
        "passwords": True, # forbid using a password similar to the top 10000 used passwords.
        "alphabet_sequence": True, # forbid a sequence of 4 or more alphabetic ordered letters, ie: abcd.
        "flash": True, # produce Flask flash messages on errors
        "long_password_override": 2, # long_password_override - number - when a password is this number times the min length, rules are not enforced. Set to 0 to disable. Default is 2
        "pwned": False, # dynamically query HIBP list of hacked and released passwords
        "show_hide_passwords": True, # allow the client to click to show the password on the page
        "min_password_length": 8 # minimum length of the password
        }
