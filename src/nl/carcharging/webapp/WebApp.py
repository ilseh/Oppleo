import datetime
import json
import logging
from nl.carcharging.config.WebAppConfig import WebAppConfig

WebAppConfig.initLogger('CarChargerWebApp')
webApplogger = logging.getLogger('nl.carcharging.webapp.WebApp')
webApplogger.debug('Initializing WebApp')

import sys
print('sys.version %s : ' % sys.version)
webApplogger.debug('sys.version %s : ' % sys.version)

WebAppConfig.loadConfig()



from flask import Flask, render_template, jsonify, redirect, request, url_for, session
from flask_login import LoginManager
from flask_socketio import SocketIO, emit
from sqlalchemy.exc import OperationalError
from sqlalchemy import event


from flask_wtf.csrf import CSRFProtect

from nl.carcharging.models.__init__ import db
from nl.carcharging.models.EnergyDeviceMeasureModel import EnergyDeviceMeasureModel
from nl.carcharging.models.Raspberry import Raspberry
from nl.carcharging.models.ChargeSessionModel import ChargeSessionModel
from nl.carcharging.models.User import User
from nl.carcharging.models.RfidModel import RfidModel
from nl.carcharging.webapp.WebSocketThread import WebSocketThread

from nl.carcharging.webapp.flaskRoutes import flaskRoutes

#import routes

# app initiliazation
app = Flask(__name__)
# Make it available through WebAppConfig
WebAppConfig.app = app

#app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config['SQLALCHEMY_DATABASE_URI'] = WebAppConfig.DATABASE_URL
app.config['EXPLAIN_TEMPLATE_LOADING'] = False
# import os; os.urandom(24)
app.config['SECRET_KEY'] = '(*^&uytwejkfh8tsefukhg23eioHJYseryg(*^5eyt123eiuyowish))!'
app.config['WTF_CSRF_SECRET_KEY'] = 'iw(*&43^%$diuYGef9872(*&*&^*&triourv2r3iouh[p2ojdkjegqrfvuytf3eYTF]oiuhwOIU'

# https://flask-wtf.readthedocs.io/en/v0.12/csrf.html
CSRFProtect(app)

# The CarCharger root flaskRoutes
app.register_blueprint(flaskRoutes) # no url_prefix

appSocketIO = SocketIO(app)
# Make it available through WebAppConfig
WebAppConfig.appSocketIO = appSocketIO

db.init_app(app)

# flask-login
WebAppConfig.login_manager = LoginManager()
WebAppConfig.login_manager.init_app(app)

wsThread = WebSocketThread()


@WebAppConfig.login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@appSocketIO.on("connect", namespace="/usage")
def connect():
    global webApplogger
    emit("server_status", "server_up")
    webApplogger.debug("Client connected...")

@appSocketIO.on("disconnect", namespace="/usage")
def disconnect():
    global webApplogger
    webApplogger.debug('Client disconnected.')

# This event currently is not used, just for reference
@appSocketIO.on('my event', namespace='/usage')
def handle_usage_event(json):
    global webApplogger
    webApplogger.debug('received json: ' + str(json))
    return ( 'one', 2 )    # client callback


@app.errorhandler(404)
def page_not_found(e):
    return render_template('errorpages/404.html'), 404


@event.listens_for(EnergyDeviceMeasureModel, 'after_update')
@event.listens_for(EnergyDeviceMeasureModel, 'after_insert')
def EnergyDeviceMeasureModel_after_insert(mapper, connection, target):
    global webApplogger
    webApplogger.debug("'after_insert' or 'after_update' event for EnergyDeviceMeasureModel")


@event.listens_for(RfidModel, 'after_update')
@event.listens_for(RfidModel, 'after_insert')
def RfidModel_after_update(mapper, connection, target):
    global webApplogger
    webApplogger.debug("'after_insert' or 'after_update' event for RfidModel")
    

if __name__ == "__main__":
    wsThread.start(appSocketIO)

    print('Starting web server on {}:{} (debug:{}, use_reloader={})...'
        .format(
            WebAppConfig.httpHost, 
            WebAppConfig.httpPort,
            WebAppConfig.DEBUG,
            WebAppConfig.useReloader
            )
        )
    webApplogger.debug('Starting web server on {}:{} (debug:{}, use_reloader={})...'
        .format(
            WebAppConfig.httpHost, 
            WebAppConfig.httpPort,
            WebAppConfig.DEBUG,
            WebAppConfig.useReloader
            )
        )
    appSocketIO.run(app, 
                    port=WebAppConfig.httpPort, 
                    debug=WebAppConfig.DEBUG, 
                    use_reloader=WebAppConfig.useReloader, 
                    host=WebAppConfig.httpHost
                    )

    wsThread.wait()

