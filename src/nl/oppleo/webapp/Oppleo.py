import datetime
import json
import logging
from nl.oppleo.models.OffPeakHoursModel import OffPeakHoursModel, Weekday
from nl.oppleo.webapp.WebSocketQueueReaderBackgroundTask import WebSocketQueueReaderBackgroundTask
from nl.oppleo.config.OppleoConfig import OppleoConfig

OppleoConfig.initLogger('Oppleo')
oppleoLogger = logging.getLogger('nl.oppleo.webapp.Oppleo')
oppleoLogger.debug('Initializing Oppleo...')

import sys
print('Reporting sys.version %s : ' % sys.version)
oppleoLogger.debug('sys.version %s : ' % sys.version)

OppleoConfig.loadConfig()

from nl.oppleo.utils.GenericUtil import GenericUtil
try:
    GPIO = GenericUtil.importGpio()
    if OppleoConfig.gpioMode == "BOARD":
        oppleoLogger.info("Setting GPIO MODE to BOARD")
        GPIO.setmode(GPIO.BOARD) if OppleoConfig.gpioMode == "BOARD" else GPIO.setmode(GPIO.BCM)
    else:
        oppleoLogger.info("Setting GPIO MODE to BCM")
        GPIO.setmode(GPIO.BCM)
except Exception as ex:
    oppleoLogger.debug("Could not setmode of GPIO, assuming dev env")

from flask import Flask, render_template, jsonify, redirect, request, url_for, session, current_app

# app initiliazation
app = Flask(__name__)
# Make it available through OppleoConfig
OppleoConfig.app = app

#app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = OppleoConfig.SQLALCHEMY_TRACK_MODIFICATIONS
app.config['SQLALCHEMY_DATABASE_URI'] = OppleoConfig.DATABASE_URL
app.config['EXPLAIN_TEMPLATE_LOADING'] = OppleoConfig.EXPLAIN_TEMPLATE_LOADING
# import os; os.urandom(24)
app.config['SECRET_KEY'] = OppleoConfig.SECRET_KEY
app.config['WTF_CSRF_SECRET_KEY'] = OppleoConfig.WTF_CSRF_SECRET_KEY

from flask_wtf.csrf import CSRFProtect
# https://flask-wtf.readthedocs.io/en/v0.12/csrf.html
CSRFProtect(app)

from flask_socketio import SocketIO, emit
appSocketIO = SocketIO(app)
# Make it available through OppleoConfig
OppleoConfig.appSocketIO = appSocketIO

# Init the database
import nl.oppleo.models.Base

from flask_login import LoginManager, current_user
import threading
from queue import Queue
from sqlalchemy.exc import OperationalError
from sqlalchemy import event

from nl.oppleo.models.EnergyDeviceMeasureModel import EnergyDeviceMeasureModel
from nl.oppleo.models.Raspberry import Raspberry
from nl.oppleo.models.ChargeSessionModel import ChargeSessionModel
from nl.oppleo.models.User import User
from nl.oppleo.models.RfidModel import RfidModel
from nl.oppleo.webapp.WebSocketThread import WebSocketThread

from nl.oppleo.daemon.MeasureElectricityUsageThread import MeasureElectricityUsageThread
from nl.oppleo.daemon.ChargerHandlerThread import ChargerHandlerThread
from nl.oppleo.daemon.PeakHoursMonitorThread import PeakHoursMonitorThread
from nl.oppleo.utils.EnergyUtil import EnergyUtil
from nl.oppleo.services.Charger import Charger
from nl.oppleo.services.LedLighter import LedLighter
from nl.oppleo.services.Buzzer import Buzzer
from nl.oppleo.services.Evse import Evse
from nl.oppleo.services.EvseReader import EvseReader

from nl.oppleo.webapp.flaskRoutes import flaskRoutes


# Create an emit queue, for other Threads to communicate to th ews emit background task
wsEmitQueue = Queue()
OppleoConfig.wsEmitQueue = wsEmitQueue


# The CarCharger root flaskRoutes
app.register_blueprint(flaskRoutes) # no url_prefix

# flask-login
OppleoConfig.login_manager = LoginManager()
OppleoConfig.login_manager.init_app(app)

threadLock = threading.Lock()
wsThread = WebSocketThread()
wsqrbBackgroundTask = WebSocketQueueReaderBackgroundTask()

wsClientCnt = 0


@OppleoConfig.login_manager.user_loader
def load_user(username):
    return User.get(username)


"""
@appSocketIO.on("connect", namespace="/usage")
def connect():
    global oppleoLogger, threadLock, wsClientCnt, wsThread, appSocketIO
    with threadLock:
        wsClientCnt += 1
        oppleoLogger.debug('socketio.connect wsClientCnt {}'.format(wsClientCnt))
        if wsClientCnt == 1:
            oppleoLogger.debug('Starting thread')
            wsThread.start(appSocketIO)
    emit("server_status", "server_up")
    oppleoLogger.debug("Client connected...")

@appSocketIO.on("disconnect", namespace="/usage")
def disconnect():
    global oppleoLogger, threadLock, wsClientCnt, wsThread, appSocketIO
    oppleoLogger.debug('Client disconnected.')
    with threadLock:
        wsClientCnt -= 1
        oppleoLogger.debug('socketio.disconnect wsClientCnt {}'.format(wsClientCnt))
        if wsClientCnt == 0:
            # stop thread
            oppleoLogger.debug('Requesting thread stop')
            wsThread.stop()
"""


@appSocketIO.on("connect", namespace="/usage")
def connect():
    global oppleoLogger, OppleoConfig, threadLock, wsClientCnt
    with threadLock:
        wsClientCnt += 1
        if request.sid not in OppleoConfig.connectedClients.keys():
            OppleoConfig.connectedClients[request.sid] = {
                                'sid'   : request.sid,
                                'auth'  : True if (current_user.is_authenticated) else False,
                                'stats' : 'connected'
                                }
    oppleoLogger.debug('socketio.connect sid: {} wsClientCnt: {} connectedClients:{}'.format( \
                    request.sid, \
                    wsClientCnt, \
                    OppleoConfig.connectedClients \
                    )
                )
    emit("server_status", "server_up")


@appSocketIO.on("disconnect", namespace="/usage")
def disconnect():
    global oppleoLogger, OppleoConfig, threadLock, wsClientCnt
    with threadLock:
        wsClientCnt -= 1
        res = OppleoConfig.connectedClients.pop(request.sid, None)
    oppleoLogger.debug('socketio.disconnect sid: {} wsClientCnt: {} connectedClients:{} res:{}'.format( \
                    request.sid, \
                    wsClientCnt, \
                    OppleoConfig.connectedClients, \
                    res
                    )
                )


@app.errorhandler(404)
def page_not_found(e):
    return render_template('errorpages/404.html'), 404


@event.listens_for(EnergyDeviceMeasureModel, 'after_update')
@event.listens_for(EnergyDeviceMeasureModel, 'after_insert')
def EnergyDeviceMeasureModel_after_insert(mapper, connection, target):
    global oppleoLogger
    oppleoLogger.debug("'after_insert' or 'after_update' event for EnergyDeviceMeasureModel")


@event.listens_for(RfidModel, 'after_update')
@event.listens_for(RfidModel, 'after_insert')
def RfidModel_after_update(mapper, connection, target):
    global oppleoLogger
    oppleoLogger.debug("'after_insert' or 'after_update' event for RfidModel")


if __name__ == "__main__":
    ##    wsThread.start(appSocketIO)

    """
    from nl.oppleo.models.OffPeakHoursModel import OffPeakHoursModel
    ohm = OffPeakHoursModel()
    ohm.test()
    """
    """
    from datetime import datetime, timedelta

    if OppleoConfig.autoSessionEnabled: 
        edmm = EnergyDeviceMeasureModel()
        kwh_used = edmm.get_usage_since(
                OppleoConfig.ENERGY_DEVICE_ID,
                (datetime.today() - timedelta(minutes=OppleoConfig.autoSessionMinutes))
                )
        if kwh_used > OppleoConfig.autoSessionEnergy:
            oppleoLogger.debug('More energy used than {}kWh in {} minutes'.format(e, t))
            oppleoLogger.debug("Keep the current session")
        else:
            oppleoLogger.debug('Less energy used than {}kWh in {} minutes'.format(e, t))
            oppleoLogger.debug("Start a new session")
    """

    """
        TESTING DETECTION OF THE END_TIME ON AUTO SESSION
    from nl.oppleo.models.EnergyDeviceMeasureModel import EnergyDeviceMeasureModel
    end_time = EnergyDeviceMeasureModel.get_time_of_kwh(
                        'laadpaal_noord',
                        '1501.6'
                        )
    end_time_str = str(end_time.strftime("%d/%m/%Y, %H:%M:%S"))
    from datetime import datetime
    now = datetime.now()
    now_str = str(now.strftime("%d/%m/%Y, %H:%M:%S"))
    """

    """
        TESTING OffPeak segments
    
    from nl.oppleo.models.OffPeakHoursModel import OffPeakHoursModel, Weekday
    segm1 = OffPeakHoursModel.get_representation(Weekday.MONDAY)
    segm2 = OffPeakHoursModel.get_representation(Weekday.SATURDAY)
    segm4 = OffPeakHoursModel.get_representation(Weekday.WEDNESDAY)

    segm3 = OffPeakHoursModel.get_all_representations_nl()
    for key, value in segm3.items(): 
        print(key, value) 
    """


    # Define the Energy Device Monitor thread and rge ChangeHandler (RFID) thread
    meuThread = MeasureElectricityUsageThread(appSocketIO)
    chThread = ChargerHandlerThread(
                    device=OppleoConfig.ENERGY_DEVICE_ID,
                    energy_util=meuThread.energyDevice.energyUtil, 
                    charger=Charger(), 
                    ledlighter=LedLighter(), 
                    buzzer=Buzzer(), 
                    evse=Evse(),
                    evse_reader=EvseReader(), 
                    appSocketIO=appSocketIO
                )
    meuThread.addCallback(chThread.energyUpdate)
    phmThread = PeakHoursMonitorThread(appSocketIO)

    OppleoConfig.meuThread = meuThread
    OppleoConfig.chThread = chThread
    OppleoConfig.phmThread = phmThread

    # Starting the web socket queue reader background task
    oppleoLogger.debug('Starting queue reader background task...')
    wsqrbBackgroundTask.start(
            appSocketIO=appSocketIO,
            wsEmitQueue=wsEmitQueue
            )

    if GenericUtil.isProd():
        # Start the Energy Device Monitor
        meuThread.start()
        # Start the RFID Monitor
        chThread.start()

    # Start the Peak Hours Monitor
    phmThread.start()


    print('Starting web server on {}:{} (debug:{}, use_reloader={})...'
        .format(
            OppleoConfig.httpHost, 
            OppleoConfig.httpPort,
            OppleoConfig.DEBUG,
            OppleoConfig.useReloader
            )
        )
    oppleoLogger.debug('Starting web server on {}:{} (debug:{}, use_reloader={})...'
        .format(
            OppleoConfig.httpHost, 
            OppleoConfig.httpPort,
            OppleoConfig.DEBUG,
            OppleoConfig.useReloader
            )
        )
    appSocketIO.run(app, 
                    port=OppleoConfig.httpPort, 
                    debug=OppleoConfig.DEBUG, 
                    use_reloader=OppleoConfig.useReloader, 
                    host=OppleoConfig.httpHost
                    )

