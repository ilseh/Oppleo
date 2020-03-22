import datetime
import json
import logging
from nl.oppleo.config.OppleoSystemConfig import OppleoSystemConfig
oppleoSystemConfig = OppleoSystemConfig()

oppleoLogger = logging.getLogger('nl.oppleo.webapp.Oppleo')
oppleoLogger.debug('Initializing Oppleo...')

import sys
print('Reporting sys.version %s : ' % sys.version)
oppleoLogger.debug('sys.version %s : ' % sys.version)

from nl.oppleo.exceptions.Exceptions import DbException
try:
    from nl.oppleo.models.Base import Base
except DbException as dbe:
    # Database could not be loaded
    pass

from nl.oppleo.models.OffPeakHoursModel import OffPeakHoursModel, Weekday
from nl.oppleo.webapp.WebSocketQueueReaderBackgroundTask import WebSocketQueueReaderBackgroundTask
from nl.oppleo.config.OppleoConfig import OppleoConfig

oppleoConfig = OppleoConfig()

from nl.oppleo.utils.GenericUtil import GenericUtil
try:
    GPIO = GenericUtil.importGpio()
    if oppleoConfig.gpioMode == "BOARD":
        oppleoLogger.info("Setting GPIO MODE to BOARD")
        GPIO.setmode(GPIO.BOARD) if oppleoConfig.gpioMode == "BOARD" else GPIO.setmode(GPIO.BCM)
    else:
        oppleoLogger.info("Setting GPIO MODE to BCM")
        GPIO.setmode(GPIO.BCM)
except Exception as ex:
    oppleoLogger.debug("Could not setmode of GPIO, assuming dev env")

from flask import Flask, render_template, jsonify, redirect, request, url_for, session, current_app

# app initiliazation
app = Flask(__name__)

# Make it available through oppleoConfig
oppleoConfig.app = app

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = oppleoSystemConfig.SQLALCHEMY_TRACK_MODIFICATIONS
app.config['SQLALCHEMY_DATABASE_URI'] = oppleoSystemConfig.DATABASE_URL
app.config['EXPLAIN_TEMPLATE_LOADING'] = oppleoSystemConfig.EXPLAIN_TEMPLATE_LOADING
# import os; os.urandom(24)
app.config['SECRET_KEY'] = oppleoConfig.secretKey
app.config['WTF_CSRF_SECRET_KEY'] = oppleoConfig.csrfSecretKey

from flask_wtf.csrf import CSRFProtect
# https://flask-wtf.readthedocs.io/en/v0.12/csrf.html
CSRFProtect(app)

from flask_socketio import SocketIO, emit
appSocketIO = SocketIO(app)
# Make it available through oppleoConfig
oppleoConfig.appSocketIO = appSocketIO

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
from nl.oppleo.utils.WebSocketUtil import WebSocketUtil


# Create an emit queue, for other Threads to communicate to th ews emit background task
wsEmitQueue = Queue()
oppleoConfig.wsEmitQueue = wsEmitQueue


# The CarCharger root flaskRoutes
app.register_blueprint(flaskRoutes) # no url_prefix

# flask-login
oppleoConfig.login_manager = LoginManager()
oppleoConfig.login_manager.init_app(app)

threadLock = threading.Lock()
wsqrbBackgroundTask = WebSocketQueueReaderBackgroundTask()

wsClientCnt = 0


@oppleoConfig.login_manager.user_loader
def load_user(username):
    return User.get(username)


@appSocketIO.on("connect", namespace="/")
def connect():
    global oppleoLogger, oppleoConfig, threadLock, wsClientCnt
    with threadLock:
        wsClientCnt += 1
        if request.sid not in oppleoConfig.connectedClients.keys():
            oppleoConfig.connectedClients[request.sid] = {
                                'sid'   : request.sid,
                                'auth'  : True if (current_user.is_authenticated) else False,
                                'stats' : 'connected'
                                }
    oppleoLogger.debug('socketio.connect sid: {} wsClientCnt: {} connectedClients:{}'.format( \
                    request.sid, \
                    wsClientCnt, \
                    oppleoConfig.connectedClients \
                    )
                )

    WebSocketUtil.emit(
            wsEmitQueue=oppleoConfig.wsEmitQueue,
            event='update', 
            id=oppleoConfig.chargerName,
            data={
                "restartRequired"   : (oppleoConfig.restartRequired or oppleoSystemConfig.restartRequired),
                "upSince"           : oppleoConfig.upSinceDatetimeStr,
                "clientsConnected"  : len(oppleoConfig.connectedClients)
            },
            namespace='/system_status',
            public=False,
            room=request.sid
        )



@appSocketIO.on("disconnect", namespace="/")
def disconnect():
    global oppleoLogger, oppleoConfig, threadLock, wsClientCnt
    with threadLock:
        wsClientCnt -= 1
        res = oppleoConfig.connectedClients.pop(request.sid, None)
    oppleoLogger.debug('socketio.disconnect sid: {} wsClientCnt: {} connectedClients:{} res:{}'.format( \
                    request.sid, \
                    wsClientCnt, \
                    oppleoConfig.connectedClients, \
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

    """
    from nl.oppleo.models.OffPeakHoursModel import OffPeakHoursModel
    ohm = OffPeakHoursModel()
    ohm.test()
    """
    """
    from datetime import datetime, timedelta

    if oppleoConfig.autoSessionEnabled: 
        edmm = EnergyDeviceMeasureModel()
        kwh_used = edmm.get_usage_since(
                oppleoConfig.chargerName,
                (datetime.today() - timedelta(minutes=oppleoConfig.autoSessionMinutes))
                )
        if kwh_used > oppleoConfig.autoSessionEnergy:
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

    """
    from nl.oppleo.config.oppleoConfigNEW import oppleoConfigNEW
    oppleoConf = oppleoConfigNEW()
    oppleoConf2 = oppleoConfigNEW()

    t1 = oppleoConf.gpioMode
    oppleoConf.gpioMode = 'BOARD'
    t2 = oppleoConf.gpioMode
    oppleoConf.gpioMode = 'BCM'
    t3 = oppleoConf.gpioMode
    try:
        oppleoConf.gpioMode = 'TEST'
    except TypeError as e:
        pass
    except ValueError as e:
        pass


    t1 = oppleoConf.pinLedRed
    try:
        oppleoConf.pinLedRed = 'TEST'
    except TypeError as e:
        pass
    t2 = oppleoConf.pinLedRed
    oppleoConf.pinLedRed = 2
    t2 = oppleoConf.pinLedRed
    """


    # Define the Energy Device Monitor thread and rge ChangeHandler (RFID) thread
    meuThread = MeasureElectricityUsageThread(appSocketIO)
    chThread = ChargerHandlerThread(
                    device=oppleoConfig.chargerName,
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

    oppleoConfig.meuThread = meuThread
    oppleoConfig.chThread = chThread
    oppleoConfig.phmThread = phmThread

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
            oppleoConfig.httpHost, 
            oppleoConfig.httpPort,
            oppleoSystemConfig.DEBUG,
            oppleoConfig.useReloader
            )
        )
    oppleoLogger.debug('Starting web server on {}:{} (debug:{}, use_reloader={})...'
        .format(
            oppleoConfig.httpHost, 
            oppleoConfig.httpPort,
            oppleoSystemConfig.DEBUG,
            oppleoConfig.useReloader
            )
        )

    WebSocketUtil.emit(
            wsEmitQueue=oppleoConfig.wsEmitQueue,
            event='update', 
            id=oppleoConfig.chargerName,
            data={
                "restartRequired": (oppleoConfig.restartRequired or oppleoSystemConfig.restartRequired),
                "upSince": oppleoConfig.upSinceDatetimeStr,
                "clientsConnected"  : len(oppleoConfig.connectedClients)
            },
            namespace='/system_status',
            public=False
        )


    appSocketIO.run(app, 
#                    port=oppleoConfig.httpPort, 
                    port=5000, 
                    debug=oppleoSystemConfig.DEBUG, 
                    use_reloader=oppleoConfig.useReloader, 
                    host=oppleoConfig.httpHost
                    )

