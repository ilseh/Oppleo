import logging
from datetime import datetime
from nl.oppleo.utils.ModulePresence import modulePresence
from nl.oppleo.config.OppleoSystemConfig import OppleoSystemConfig
oppleoSystemConfig = OppleoSystemConfig()
oppleoConfig = None

oppleoLogger = logging.getLogger('nl.oppleo.webapp.Oppleo')
oppleoLogger.debug('Initializing Oppleo...')

import sys
print('Reporting sys.version %s : ' % sys.version)
oppleoLogger.debug('sys.version %s : ' % sys.version)

from nl.oppleo.exceptions.Exceptions import DbException

from functools import wraps

try:
    from nl.oppleo.models.Base import Base
    from nl.oppleo.webapp.WebSocketQueueReaderBackgroundTask import WebSocketQueueReaderBackgroundTask
    from nl.oppleo.config.OppleoConfig import OppleoConfig
    oppleoConfig = OppleoConfig()
    oppleoSystemConfig.chargerID = oppleoConfig.chargerID

    from nl.oppleo.services.PushMessage import PushMessage

    if modulePresence.gpioAvailable():
        GPIO = modulePresence.GPIO
        try:
            if oppleoConfig.gpioMode == "BOARD":
                oppleoLogger.info("Setting GPIO MODE to BOARD")
                GPIO.setmode(GPIO.BOARD)
            else:
                oppleoLogger.info("Setting GPIO MODE to BCM")
                GPIO.setmode(GPIO.BCM)
            # No warnings
            GPIO.setwarnings(False)
        except Exception as e:
            oppleoLogger.debug("Could not setmode of GPIO, assuming dev env")

    from flask import Flask, render_template, jsonify, redirect, request, url_for, session, current_app

    # app initiliazation
    app = Flask(__name__)

    # Make it available through oppleoConfig
    oppleoConfig.app = app

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = oppleoSystemConfig.SQLALCHEMY_TRACK_MODIFICATIONS
    app.config['SQLALCHEMY_DATABASE_URI'] = oppleoSystemConfig.DATABASE_URL
    app.config['EXPLAIN_TEMPLATE_LOADING'] = oppleoSystemConfig.EXPLAIN_TEMPLATE_LOADING
    app.config['SQLALCHEMY_POOL_RECYCLE'] = 3600
    # import os; os.urandom(24)
    app.config['SECRET_KEY'] = oppleoConfig.secretKey
    app.config['WTF_CSRF_SECRET_KEY'] = oppleoConfig.csrfSecretKey

    # File upload, used for user image
    app.config['AVATAR_FOLDER'] = oppleoConfig.oppleoRootDirectory + 'src/nl/oppleo/webapp/static/images/avatars/'
    app.config['VEHICLE_FOLDER'] = oppleoConfig.oppleoRootDirectory + 'src/nl/oppleo/webapp/static/images/vehicles/'
    app.config['MAX_CONTENT_PATH'] = 256 * 1024  # 256kB


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
    from nl.oppleo.services.HomeAssistantMqttHandlerThread import HomeAssistantMqttHandlerThread 
    
    from nl.oppleo.services.Buzzer import Buzzer
    from nl.oppleo.services.EvseOutput import EvseOutput
    from nl.oppleo.services.EvseReader import EvseReader

    from nl.oppleo.webapp.flaskRoutes import flaskRoutes
    from nl.oppleo.utils.OutboundEvent import OutboundEvent

    from nl.oppleo.utils.BackupUtil import BackupUtil

    # Create an emit queue, for other Threads to communicate to th ews emit background task
    wsEmitQueue = Queue()
    oppleoConfig.wsEmitQueue = wsEmitQueue
    oppleoSystemConfig.wsEmitQueue = wsEmitQueue

    # The Oppleo root flaskRoutes
    app.register_blueprint(flaskRoutes) # no url_prefix

    # flask-login
    oppleoConfig.login_manager = LoginManager()
    oppleoConfig.login_manager.init_app(app)

    threadLock = threading.Lock()
    wsqrbBackgroundTask = WebSocketQueueReaderBackgroundTask()

    wsClientCnt = 0

    # Resource is only served for logged in user if allowed in preferences
    def config_dashboard_access_restriction(function):
        @wraps(function)
        def decorated(*args, **kwargs):
            # Allow dashboard and Usage table access if unrestructed in config
            # request.remote_addr - returns remote address, or IP of reverse proxy
            # request.headers.get('X-Forwarded-For') - returns router address (router is behind the reverse proxy)

            if (not oppleoConfig.restrictDashboardAccess or \
                ( oppleoConfig.allowLocalDashboardAccess and request.remote_addr != oppleoConfig.routerIPAddress ) or \
                current_user.is_authenticated):
                return function(*args, **kwargs)
            # return abort(403) # unauthenticated
            # Not allowed.
            # delete old - never used - cookie
            if 'login_next' in session:
                del session['login_next']
            # if somehow ended up at logout, don't forward to login
            if (request.endpoint == "flaskRoutes.logout"):
                return redirect(url_for('flaskRoutes.home'))
            ignore_login_next = bool(request.headers.get('ignore-login-next'))
            if not ignore_login_next:
                # Redirect to login but rememmber the original request 
                session['login_next'] = request.full_path
                return redirect(url_for('flaskRoutes.login'))
            return ('Niet ingelogd', 401)
        return decorated

    @oppleoConfig.login_manager.user_loader
    def load_user(username):
        return User.get(username)

    @appSocketIO.on("connect", namespace="/system_status")
    @appSocketIO.on("connect", namespace="/charge_session")
    @appSocketIO.on("connect", namespace="/usage")
    @appSocketIO.on("connect", namespace="/evse_status")
    @appSocketIO.on("connect", namespace="/backup")
    @appSocketIO.on("connect", namespace="/mqtt")
    @appSocketIO.on("connect", namespace="/settings")
    #@appSocketIO.on("connect", namespace="/")
    @config_dashboard_access_restriction
    def connect(*args, **kwargs):
        global oppleoLogger, oppleoConfig, threadLock, wsClientCnt, oppleoSystemConfig

        with threadLock:
            wsClientCnt += 1
            if request.sid not in oppleoConfig.connectedClients.keys():
                oppleoConfig.connectedClients[request.sid] = {
                                    'sid'       : request.sid,
                                    'auth'      : True if (current_user.is_authenticated) else False,
                                    'stats'     : 'connected',
                                    'namespace' : request.namespace if request.namespace is not None else 'UNKNOWN'
                                    }
        oppleoLogger.debug('socketio.connect sid: {} wsClientCnt: {} connectedClients:{}'.format( \
                        request.sid, \
                        wsClientCnt, \
                        oppleoConfig.connectedClients \
                        )
                    )
        if oppleoSystemConfig.mqttOutboundEnabled:
            OutboundEvent.emitMQTTEvent( event='connect',
                                        data={
                                            "clientId"          : request.sid,
                                            'auth'              : True if (current_user.is_authenticated) else False,
                                            'namespace'         : request.namespace if request.namespace is not None else 'UNKNOWN',
                                            "clientsConnected"  : len(oppleoConfig.connectedClients)
                                        },
                                        id=oppleoConfig.chargerID,
                                        namespace='/websocket'
                                        )
        OutboundEvent.triggerEvent(
                event='update', 
                id=oppleoConfig.chargerID,
                data={
                    "restartRequired"   : (oppleoConfig.restartRequired or oppleoSystemConfig.restartRequired),
                    "upSince"           : oppleoConfig.upSinceDatetimeStr,
                    "clientsConnected"  : len(oppleoConfig.connectedClients)
                },
                namespace='/system_status',
                public=False,
                room=request.sid
            )



    @appSocketIO.on("disconnect", namespace="/system_status")
    @appSocketIO.on("disconnect", namespace="/charge_session")
    @appSocketIO.on("disconnect", namespace="/usage")
    @appSocketIO.on("disconnect", namespace="/evse_status")
    @appSocketIO.on("disconnect", namespace="/backup")
    @appSocketIO.on("disconnect", namespace="/mqtt")
    @appSocketIO.on("disconnect", namespace="/settings")
    #@appSocketIO.on("disconnect", namespace="/")
    @config_dashboard_access_restriction
    def disconnect():
        global oppleoLogger, oppleoConfig, threadLock, wsClientCnt, oppleoSystemConfig

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
        if oppleoSystemConfig.mqttOutboundEnabled:
            OutboundEvent.emitMQTTEvent( event='disconnect',
                                        data={
                                            "clientId"          : request.sid,
                                            'namespace'         : request.namespace if request.namespace is not None else 'UNKNOWN',
                                            "clientsConnected"  : len(oppleoConfig.connectedClients)
                                        },
                                        id=oppleoConfig.chargerID,
                                        namespace='/websocket'
                                        )



    # 404 Not Found - The server can not find requested resource.
    @app.errorhandler(404)
    def app_page_not_found(e):
        return render_template('errorpages/404.html'), 404

    # 409 Conflict - This response is sent when a request conflicts with the current state of the server.
    @app.errorhandler(409)
    def app_conflict(e):
        return render_template('errorpages/409.html'), 409

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

        # Define the Energy Device Monitor thread and the ChangeHandler (RFID) thread
        meuThread = None

        try:
            meuThread = MeasureElectricityUsageThread(appSocketIO)
        except Exception as e:
            oppleoLogger.error("MeasureElectricityUsageThread failed - no energy measurements. Details:{}".format(str(e)))

        chThread = None
        try:
            chThread = ChargerHandlerThread(
                        device=oppleoConfig.chargerID,
                        buzzer=Buzzer(), 
                        evseOutput=EvseOutput(),
                        evseReader=EvseReader(), 
                        appSocketIO=appSocketIO
                    )
        except Exception as e:
            oppleoLogger.error("ChargerHandlerThread failed - no charger management. Details:{}".format(str(e)))

        if meuThread is not None and chThread is not None:
            meuThread.addCallback(chThread.energyUpdate)

        oppleoConfig.meuThread = meuThread
        oppleoConfig.chThread = chThread

        phmThread = None
        phmThread = PeakHoursMonitorThread(appSocketIO)
        oppleoConfig.phmThread = phmThread

        if oppleoConfig.backupEnabled:
            backupUtil = BackupUtil()
            backupUtil.startBackupMonitorThread()

        # Starting the web socket queue reader background task
        oppleoLogger.debug('Starting queue reader background task...')
        wsqrbBackgroundTask.start(
                appSocketIO=appSocketIO,
                wsEmitQueue=wsEmitQueue
                )

        # Start the Energy Device Monitor
        if meuThread is not None:
            meuThread.start()
            pass
        else:
            oppleoLogger.warning("MeasureElectricityUsageThread not started.")
        # Start the RFID Monitor
        if chThread is not None:
            chThread.start()
            pass
        else:
            oppleoLogger.warning("ChargerHandlerThread not started.")

        # Start the Peak Hours Monitor
        phmThread.start()

        print('Starting web server on {}:{} (debug:{}, use_reloader={})...'
            .format(
                oppleoSystemConfig.httpHost, 
                oppleoSystemConfig.httpPort,
                oppleoSystemConfig.DEBUG,
                oppleoConfig.useReloader
                )
            )
        oppleoLogger.debug('Starting web server on {}:{} (debug:{}, use_reloader={})...'
            .format(
                oppleoSystemConfig.httpHost, 
                oppleoSystemConfig.httpPort,
                oppleoSystemConfig.DEBUG,
                oppleoConfig.useReloader
                )
            )

        OutboundEvent.triggerEvent(
                event='update', 
                id=oppleoConfig.chargerID,
                data={
                    "restartRequired": (oppleoConfig.restartRequired or oppleoSystemConfig.restartRequired),
                    "upSince": oppleoConfig.upSinceDatetimeStr,
                    "clientsConnected"  : len(oppleoConfig.connectedClients)
                },
                namespace='/system_status',
                public=False
            )

        PushMessage.sendMessage(
            "Starting", 
            "Starting Oppleo {} at {}."
            .format(
                oppleoConfig.chargerID,
                datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
                )
            )

        homeAssistantMqttHandlerThread = HomeAssistantMqttHandlerThread()

        if meuThread is not None:
            meuThread.addCallback(homeAssistantMqttHandlerThread.energyUpdate)

        # Loop the thread
        homeAssistantMqttHandlerThread.start()

        appSocketIO.run(app, 
            port=oppleoSystemConfig.httpPort, 
            debug=oppleoSystemConfig.DEBUG, 
            use_reloader=oppleoConfig.useReloader, 
            host=oppleoSystemConfig.httpHost
            )

        PushMessage.sendMessage(
            "Terminating", 
            "Terminating Oppleo {} at {}."
            .format(
                oppleoConfig.chargerID,
                datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
                )
            )


except DbException as dbe:
    # Database could not be loaded - run error page app
    oppleoLogger.error('DbException stopped Oppleo!')

    if __name__ == '__main__':
        oppleoLogger.error('Running Oppleo in limp mode...')

        from flask import Flask, render_template, jsonify, redirect, request, url_for, session, current_app
        from werkzeug.serving import run_simple
        import os
        from flask_wtf.csrf import CSRFProtect

        limpApp = Flask(__name__)

        limpApp.config['EXPLAIN_TEMPLATE_LOADING'] = True
        secret = os.urandom(24)
        limpApp.config['SECRET_KEY'] = secret
        limpApp.config['WTF_CSRF_SECRET_KEY'] = secret

        # https://flask-wtf.readthedocs.io/en/v0.12/csrf.html
        CSRFProtect(limpApp)

        @limpApp.errorhandler(400)
        def limp_page_not_found(e):
            oppleoLogger.debug('400 bad request error handler')
            return render_template('errorpages/400.html'), 400

        @limpApp.errorhandler(404)
        def limp_bad_request(e):
            oppleoLogger.debug('404 page not found error handler')
            return render_template('errorpages/404.html'), 404

        @limpApp.errorhandler(500)
        def limp_internal_server_error(e):
            oppleoLogger.debug('500 internal_server_error error handler')
            return render_template('errorpages/500.html'), 500

        # Standard return error 500 - Internal Server Error
        @limpApp.route("/")
        def limp_index():
            return render_template('errorpages/503-DbException.html',
                restart_allowed=True if oppleoSystemConfig.onDbFailureAllowRestart else False
                ), 503

        from nl.oppleo.webapp.AuthorizeForm import AuthorizeForm
        @limpApp.route("/restart", methods=["GET", "POST"])
        def limp_restart():
            global oppleoSystemConfig, oppleoLogger
            oppleoLogger.debug('/restart {}'.format(request.method))

            if not oppleoSystemConfig.onDbFailureAllowRestart:
                # Not alowed, show regular page
                return redirect(url_for('limpApp.index'))

            # For GET requests, display the authorize form. 
            form = AuthorizeForm()
            if (request.method == 'GET'):
                if oppleoSystemConfig.onDbFailureShowCurrentUrl:
                    form.extra_field.data = oppleoSystemConfig.DATABASE_URL
                return render_template("authorize.html", 
                    form=form,
                    requesttitle="Herstarten",
                    extra_field_enabled= True if oppleoSystemConfig.onDbFailureAllowUrlChange else False,
                    extra_field_placeholder="postgresql://db_user:db_password@hostname:5432/db_name",
                    extra_field_description="Geef optioneel een nieuwe database URL",
                    extra_field_icon="fas fa-database",
                    password_field_description="Voer het MAGIC wachtwoord in",
                    requestdescription="Herstel eerst de database of pas de database URL aan, en herstart daarna Oppleo hieronder op te proberen de koppeling met de database te herstellen. <br/>Het herstarten van oppleo duurt ongeveer 10 seconden.",
                    buttontitle="Herstart!"
                    )

            # For POST requests, process the form.
            if form.validate_on_submit() and \
                oppleoSystemConfig.onDbFailureMagicPasswordCheck(form.password.data):
                oppleoLogger.debug('Restart requested and authorized.')
                if oppleoSystemConfig.onDbFailureAllowUrlChange and               \
                    ( (oppleoSystemConfig.onDbFailureShowCurrentUrl and           \
                      form.extra_field.data != oppleoSystemConfig.DATABASE_URL)   \
                    or ( not oppleoSystemConfig.onDbFailureShowCurrentUrl and     \
                      form.extra_field.data != '')                                \
                    ):
                    # New database URL, try that
                    oppleoLogger.debug('Changing DATABASE_URL')
                    oppleoSystemConfig.DATABASE_URL = form.extra_field.data
                # Simple os.system('sudo systemctl restart Oppleo.service') initiates restart before a webpage can be returned
                oppleoLogger.debug('Restarting in 2 seconds...')
                try:
                    os.system("nohup sudo -b bash -c 'sleep 2; systemctl restart Oppleo.service' &>/dev/null")
                except Exception as e:
                    oppleoLogger.warning('Restart failed: {}'.format(str(e)))
                return render_template("restarting.html")
            else:
                return render_template("authorize.html", 
                        form=form, 
                        requesttitle="Herstarten",
                        extra_field_enabled= True if oppleoSystemConfig.onDbFailureAllowUrlChange else False,
                        extra_field_placeholder="postgresql://db_user:db_password@hostname:5432/db_name",
                        extra_field_description="Geef optioneel een nieuwe database URL",
                        extra_field_icon="fas fa-database",
                        password_field_description="Voer het MAGIC wachtwoord in",
                        requestdescription="Herstel de database of de URL en herstart de applicatie. Het herstarten van Oppleo duurt ongeveer 10 seconden.",
                        buttontitle="Herstart!",
                        errormsg="Het MAGIC wachtwoord is onjuist"
                        )

        # Oppleo Limp mode Prowl apiKey and no chargerID
        if oppleoSystemConfig.prowlEnabled:
            from nl.oppleo.services.PushMessageProwl import PushMessageProwl
            PushMessageProwl.sendMessage(
                title="Limp mode", 
                message="Database exception caused limp mode at {}. [signature: {}]"
                    .format(
                        datetime.now().strftime("%d/%m/%Y, %H:%M:%S"),
                        oppleoSystemConfig.SIGNATURE
                    ),
                priority=PushMessageProwl.priorityHigh,
                apiKey=oppleoSystemConfig.prowlApiKey,
                chargerName='Unknown'
                )

        # Oppleo Limp mode Prowl apiKey and no chargerID
        if oppleoSystemConfig.pushoverEnabled:
            from nl.oppleo.services.PushMessagePushover import PushMessagePushover
            PushMessagePushover.sendMessage(
                title="Limp mode", 
                message="Database exception caused limp mode at {}. [signature: {}]"
                    .format(
                        datetime.now().strftime("%d/%m/%Y, %H:%M:%S"),
                        oppleoSystemConfig.SIGNATURE
                    ),
                priority=PushMessagePushover.priorityHigh,
                apiKey=oppleoSystemConfig.pushoverApiKey,
                userKey=oppleoSystemConfig.pushoverUserKey,
                device=oppleoSystemConfig.pushoverDevice,
                sound=oppleoSystemConfig.pushoverSound,
                chargerName='Unknown'
                )

        run_simple(
            oppleoSystemConfig.httpHost,
            oppleoSystemConfig.httpPort,
            limpApp,
            use_reloader=False, 
            use_debugger=True, 
            use_evalex=True
            )


except Exception as e:
    import traceback
    traceback.print_exc()
    # Any exception raised - restart app
    oppleoLogger.error('Exception stopped Oppleo! Details:{}'.format(str(e)))
    from os import system
    from nl.oppleo.services.PushMessageProwl import PushMessageProwl

    restartFailed = True
    if __name__ == '__main__' and hasattr(e, 'errno') and e.errno != 48:
        oppleoLogger.error('Restarting Oppleo...')
        restartFailed = False

        # Simple os.system('sudo systemctl restart Oppleo.service') initiates restart before a webpage can be returned
        oppleoLogger.debug('Restarting in 30 seconds...')
        try:
            system("nohup sudo -b bash -c 'sleep 30; systemctl restart Oppleo.service' &>/dev/null")
        except Exception:
            restartFailed = True
    else:
        oppleoLogger.error('Cannot recover Oppleo...')

    # Hardcoded Oppleo Limp mode Prowl apiKey and no chargerID
    if oppleoSystemConfig.prowlEnabled:
        from nl.oppleo.services.PushMessageProwl import PushMessageProwl
        PushMessageProwl.sendMessage(
            title="Crashed" if restartFailed else "Restarting", 
            message="An exception caused a restart at {}. (signature: {} Exception details: {}{})"
                .format(
                    datetime.now().strftime("%d/%m/%Y, %H:%M:%S"),
                    oppleoSystemConfig.SIGNATURE,
                    str(e),
                    '' if oppleoConfig is None or not isinstance(oppleoConfig.chargerNameText, str) else ' chargerName: {}'.format(oppleoConfig.chargerNameText)
                ),
            priority=PushMessageProwl.priorityHigh,
            apiKey=oppleoSystemConfig.prowlApiKey,
            chargerName='Unknown' if oppleoConfig is None or not isinstance(oppleoConfig.chargerNameText, str) else oppleoConfig.chargerNameText
            )

    if oppleoSystemConfig.pushoverEnabled:
        from nl.oppleo.services.PushMessagePushover import PushMessagePushover
        PushMessagePushover.sendMessage(
            title="Crashed" if restartFailed else "Restarting", 
            message="An exception caused a restart at {}. (signature: {} Exception details: {}{})"
                .format(
                    datetime.now().strftime("%d/%m/%Y, %H:%M:%S"),
                    oppleoSystemConfig.SIGNATURE,
                    str(e),
                    '' if oppleoConfig is None or not isinstance(oppleoConfig.chargerNameText, str) else ' chargerName: {}'.format(oppleoConfig.chargerNameText)
                ),
            priority=PushMessagePushover.priorityHigh,
            apiKey=oppleoSystemConfig.pushoverApiKey,
            userKey=oppleoSystemConfig.pushoverUserKey,
            device=oppleoSystemConfig.pushoverDevice,
            sound=oppleoSystemConfig.pushoverSound,
            chargerName='Unknown'
            )
