import datetime
import json
import logging
from nl.carcharging.webapp.WebSocketQueueReaderBackgroundTask import WebSocketQueueReaderBackgroundTask
from nl.carcharging.config.WebAppConfig import WebAppConfig

WebAppConfig.initLogger('CarChargerWebApp')
webApplogger = logging.getLogger('nl.carcharging.webapp.WebApp')
webApplogger.debug('Initializing WebApp')

import sys
print('Reporting sys.version %s : ' % sys.version)
webApplogger.debug('sys.version %s : ' % sys.version)

WebAppConfig.loadConfig()

from nl.carcharging.utils.GenericUtil import GenericUtil
try:
    GPIO = GenericUtil.importGpio()
    if WebAppConfig.gpioMode == "BOARD":
        webApplogger.info("Setting GPIO MODE to BOARD")
        GPIO.setmode(GPIO.BOARD) if WebAppConfig.gpioMode == "BOARD" else GPIO.setmode(GPIO.BCM)
    else:
        webApplogger.info("Setting GPIO MODE to BCM")
        GPIO.setmode(GPIO.BCM)
except Exception as ex:
    webApplogger.debug("Could not setmode of GPIO, assuming dev env")

from flask import Flask, render_template, jsonify, redirect, request, url_for, session, current_app

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

from flask_wtf.csrf import CSRFProtect
# https://flask-wtf.readthedocs.io/en/v0.12/csrf.html
CSRFProtect(app)

from flask_socketio import SocketIO, emit
appSocketIO = SocketIO(app)
# Make it available through WebAppConfig
WebAppConfig.appSocketIO = appSocketIO

# Init the database
import nl.carcharging.models.Base

from flask_login import LoginManager
import threading
from queue import Queue
from sqlalchemy.exc import OperationalError
from sqlalchemy import event

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

from nl.carcharging.webapp.flaskRoutes import flaskRoutes


# Create an emit queue, for other Threads to communicate to th ews emit background task
wsEmitQueue = Queue()
WebAppConfig.wsEmitQueue = wsEmitQueue


# The CarCharger root flaskRoutes
app.register_blueprint(flaskRoutes) # no url_prefix

# flask-login
WebAppConfig.login_manager = LoginManager()
WebAppConfig.login_manager.init_app(app)

threadLock = threading.Lock()
wsThread = WebSocketThread()
wsqrbBackgroundTask = WebSocketQueueReaderBackgroundTask()

wsClientCnt = 0


@WebAppConfig.login_manager.user_loader
def load_user(username):
    return User.get(username)


"""
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
"""


@appSocketIO.on("connect", namespace="/usage")
def connect():
    global webApplogger, threadLock, wsClientCnt
    with threadLock:
        wsClientCnt += 1
    webApplogger.debug('socketio.connect wsClientCnt {}'.format(wsClientCnt))
    emit("server_status", "server_up")


@appSocketIO.on("disconnect", namespace="/usage")
def disconnect():
    global webApplogger, threadLock, wsClientCnt
    with threadLock:
        wsClientCnt -= 1
    webApplogger.debug('socketio.disconnect wsClientCnt {}'.format(wsClientCnt))


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

    """
    from nl.carcharging.models.OffPeakHoursModel import OffPeakHoursModel
    ohm = OffPeakHoursModel()
    ohm.test()
    """
    """
    from datetime import datetime, timedelta

    if WebAppConfig.autoSessionEnabled: 
        edmm = EnergyDeviceMeasureModel()
        kwh_used = edmm.get_usage_since(
                WebAppConfig.ENERGY_DEVICE_ID,
                (datetime.today() - timedelta(minutes=WebAppConfig.autoSessionMinutes))
                )
        if kwh_used > WebAppConfig.autoSessionEnergy:
            webApplogger.debug('More energy used than {}kWh in {} minutes'.format(e, t))
            webApplogger.debug("Keep the current session")
        else:
            webApplogger.debug('Less energy used than {}kWh in {} minutes'.format(e, t))
            webApplogger.debug("Start a new session")
    """

    # Define the Energy Device Monitor thread and rge ChangeHandler (RFID) thread
    meuThread = MeasureElectricityUsageThread(appSocketIO)
    chThread = ChargerHandlerThread(
                    device=WebAppConfig.ENERGY_DEVICE_ID,
                    energy_util=meuThread.energyDevice.energyUtil, 
                    charger=Charger(), 
                    ledlighter=LedLighter(), 
                    buzzer=Buzzer(), 
                    evse=Evse(),
                    evse_reader=EvseReader(), 
                    appSocketIO=appSocketIO
                )
    meuThread.addCallback(chThread.energyUpdate)
    WebAppConfig.meuThread = meuThread
    WebAppConfig.chThread = chThread

    # Starting the web socket queue reader background task
    webApplogger.debug('Starting queue reader background task...')
    wsqrbBackgroundTask.start(
            appSocketIO=appSocketIO,
            wsEmitQueue=wsEmitQueue
            )

    """
    device_measurement = EnergyDeviceMeasureModel().get_last_saved(WebAppConfig.ENERGY_DEVICE_ID)
    from nl.carcharging.utils.WebSocketUtil import WebSocketUtil
    WebSocketUtil.emit(
            event='status_update',
            data=device_measurement.to_str(),
            namespace='/usage'
        )
    while True:
        appSocketIO.sleep(1)
        pass
    """

    if GenericUtil.isProd():
        # Start the Energy Device Monitor
        meuThread.start()
        # Start the RFID Monitor
        chThread.start()

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

