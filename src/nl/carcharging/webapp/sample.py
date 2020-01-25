import os
import logging
from flask import Flask
from nl.carcharging.config.WebAppConfig import WebAppConfig


flaskApp = Flask(__name__)


WebAppConfig.sqlalchemy_engine = 123

print("ahum %s " % WebAppConfig.PARAM_ENV)

print("os.getenv(WebAppConfig.PARAM_ENV) %s" % os.getenv('CARCHARGING_ENV'))

"""
flaskApp.config.from_object(
    WebAppConfig.env[os.getenv(WebAppConfig.PARAM_ENV)]
)
"""

@flaskApp.route('/')
def index():
    return "<span style='color:red'>In carcharger/webapp dir A0023</span>"

