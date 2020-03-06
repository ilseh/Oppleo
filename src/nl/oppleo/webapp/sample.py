import os
import logging
from flask import Flask
from nl.oppleo.config.OppleoConfig import OppleoConfig


flaskApp = Flask(__name__)


OppleoConfig.sqlalchemy_engine = 123

print("ahum %s " % OppleoConfig.PARAM_ENV)

print("os.getenv(OppleoConfig.PARAM_ENV) %s" % os.getenv('oppleo_ENV'))

"""
flaskApp.config.from_object(
    OppleoConfig.env[os.getenv(OppleoConfig.PARAM_ENV)]
)
"""

@flaskApp.route('/')
def index():
    return "<span style='color:red'>In carcharger/webapp dir A0023</span>"

