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
from threading import Lock
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

from nl.carcharging.daemon.MeasureElectricityUsageThread import MeasureElectricityUsageThread
from nl.carcharging.daemon.ChargerHandlerThread import ChargerHandlerThread
from nl.carcharging.utils.EnergyUtil import EnergyUtil
from nl.carcharging.services.Charger import Charger
from nl.carcharging.services.LedLighter import LedLighter
from nl.carcharging.services.Buzzer import Buzzer
from nl.carcharging.services.Evse import Evse
from nl.carcharging.services.EvseReader import EvseReader
from nl.carcharging.utils.UpdateOdometerTeslaUtil import UpdateOdometerTeslaUtil

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

threadLock = Lock()
wsThread = WebSocketThread()

wsClientCnt = 0


@WebAppConfig.login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@appSocketIO.on("connect", namespace="/usage")
def connect():
    global webApplogger, threadLock, wsClientCnt, wsThread, appSocketIO
    with threadLock:
        wsClientCnt += 1
        webApplogger.debug('socketio.connect wsClientCnt {}'.format(wsClientCnt))
        if wsClientCnt == 1:
            webApplogger.debug('Starting thread')
            wsThread.start(appSocketIO)
    emit("server_status", "server_up")
    webApplogger.debug("Client connected...")

@appSocketIO.on("disconnect", namespace="/usage")
def disconnect():
    global webApplogger, threadLock, wsClientCnt, wsThread, appSocketIO
    webApplogger.debug('Client disconnected.')
    with threadLock:
        wsClientCnt -= 1
        webApplogger.debug('socketio.disconnect wsClientCnt {}'.format(wsClientCnt))
        if wsClientCnt == 0:
            # stop thread
            webApplogger.debug('Requesting thread stop')
            wsThread.stop()


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
    ##    wsThread.start(appSocketIO)

    # Start the Energy Device Monitor
#    meuThread = MeasureElectricityUsageThread()
#    meuThread.start(appSocketIO)

    # Start the RFID Monitor
    chThread = ChargerHandlerThread(
                    energy_util=EnergyUtil(), 
                    charger=Charger(), 
                    ledlighter=LedLighter(), 
                    buzzer=Buzzer(), 
                    evse=Evse(),
                    evse_reader=EvseReader(), 
                    tesla_util=UpdateOdometerTeslaUtil()
                )
    chThread.start(appSocketIO)


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

