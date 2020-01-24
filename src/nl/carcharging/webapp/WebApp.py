import datetime
import json
import os
import logging
from nl.carcharging.config.WebAppConfig import WebAppConfig

WebAppConfig.initLogger('CarChargerWebApp')
logger = logging.getLogger('nl.carcharging.webapp.WebApp')
logger.debug('Initializing WebApp')

try:
    import uwsgidecorators
except ModuleNotFoundError:
    logger.debug('! uwsgi and uwsgidecorators not loaded, not running under uWSGI...')
from functools import wraps

from flask import Flask, render_template, jsonify, redirect, request, url_for, session
from flask_login import LoginManager
from flask_socketio import SocketIO, emit
from sqlalchemy.exc import OperationalError
from sqlalchemy import event


from flask_wtf.csrf import CsrfProtect

from nl.carcharging.models import db
from nl.carcharging.models.EnergyDeviceMeasureModel import EnergyDeviceMeasureModel
from nl.carcharging.models.Raspberry import Raspberry
from nl.carcharging.models.ChargeSessionModel import ChargeSessionModel
from nl.carcharging.models.User import User
from nl.carcharging.models.EnergyDeviceMeasureModel import EnergyDeviceMeasureModel
from nl.carcharging.models.RfidModel import RfidModel
# TEST
from nl.carcharging.utils.UpdateOdometerTeslaUtil import UpdateOdometerTeslaUtil

from nl.carcharging.webapp.flaskRoutes import flaskRoutes

#import routes

# app initiliazation
flaskApp = Flask(__name__)
# Make it available through WebAppConfig
WebAppConfig.flaskApp = flaskApp

flaskApp.config.from_object(
    WebAppConfig.env[os.getenv(WebAppConfig.PARAM_ENV)]
)
#flaskApp.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
flaskApp.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
# import os; os.urandom(24)
flaskApp.config['SECRET_KEY'] = '(*^&uytwejkfh8tsefukhg23eioHJYseryg(*^5eyt123eiuyowish))!'
flaskApp.config['WTF_CSRF_SECRET_KEY'] = 'iw(*&43^%$diuYGef9872(*&*&^*&triourv2r3iouh[p2ojdkjegqrfvuytf3eYTF]oiuhwOIU'

# https://flask-wtf.readthedocs.io/en/v0.12/csrf.html
CsrfProtect(flaskApp)

# The CarCharger root flaskRoutes
flaskApp.register_blueprint(flaskRoutes) # no url_prefix

flaskAppSocketIO = SocketIO(flaskApp)
# Make it available through WebAppConfig
WebAppConfig.flaskAppSocketIO = flaskAppSocketIO

db.init_app(flaskApp)

# flask-login
WebAppConfig.login_manager = LoginManager()
WebAppConfig.login_manager.init_app(flaskApp)


class WebSocketThread(object):
    # Count the message updates send through the websocket
    counter = 1
    most_recent = ""

    def __init__(self):
        self.logger = logging.getLogger('nl.carcharging.models.SessionModel')
        self.logger.debug('Initializing SessionModel without data')

        self.thread = None

    def websocket_start(self):
        logger.debug('Starting background task...')
        while True:
            flaskAppSocketIO.sleep(7)
            try:
                self.websocket_send_usage_update("status_update")
            except OperationalError as e:
                # If the database is unavailable (or no access allowed),
                # remain running untill the access is restored
                logger.debug(f'Something wrong with the database! {e}')

    def start(self):
        logger.debug('Launching background task...')
        self.thread = flaskAppSocketIO.start_background_task(self.websocket_start)

    def websocket_send_usage_update(self, type):
        logger.debug('Checking usage data...')

        device_measurement = EnergyDeviceMeasureModel()  
        device_measurement.energy_device_id = "laadpaal_noord"
        qr = device_measurement.get_last_saved(energy_device_id="laadpaal_noord")
        if (self.most_recent != qr.get_created_at_str()):
            logger.debug(f'Send msg {self.counter} via websocket...')
            flaskAppSocketIO.emit('status_update', { 'data': qr.to_str() }, namespace='/usage')
            self.most_recent = qr.get_created_at_str()
        else:
            logger.debug('No change in usage at this time.')

        self.counter += 1

    def wait(self):
        self.thread.join()


@WebAppConfig.login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@flaskAppSocketIO.on("connect", namespace="/usage")
def connect():
    emit("server_status", "server_up")
    logger.debug("Client connected...")

@flaskAppSocketIO.on("disconnect", namespace="/usage")
def disconnect():
    logger.debug('Client disconnected.')

# This event currently is not used, just for reference
@flaskAppSocketIO.on('my event', namespace='/usage')
def handle_usage_event(json):
    logger.debug('received json: ' + str(json))
    return ( 'one', 2 )    # client callback


@flaskApp.errorhandler(404)
def page_not_found(e):
    return render_template('errorpages/404.html'), 404

try:
    @uwsgidecorators.postfork
    def postFork():
        logger.debug('postFork()')
        wsThread = WebSocketThread()
        logger.debug('Starting Web Sockets...')
        wsThread.start()
        wsThread.wait()
except NameError:
    logger.debug("! @uwsgidecorators.postfork excluded...")


@event.listens_for(EnergyDeviceMeasureModel, 'after_update')
@event.listens_for(EnergyDeviceMeasureModel, 'after_insert')
def EnergyDeviceMeasureModel_after_insert(mapper, connection, target):
    logger.debug("'after_insert' or 'after_update' event for EnergyDeviceMeasureModel")


@event.listens_for(RfidModel, 'after_update')
@event.listens_for(RfidModel, 'after_insert')
def RfidModel_after_update(mapper, connection, target):
    logger.debug("'after_insert' or 'after_update' event for RfidModel")


if __name__ == "__main__":
    wsThread = WebSocketThread()
    wsThread.start()

    """
    # Just as a test
    uotu = UpdateOdometerTeslaUtil()
    uotu.set_charge_session_id(12)
    uotu.start()
    """
    
    logger.debug('Starting web server...')
    flaskAppSocketIO.run(flaskApp, port=5000, debug=True, use_reloader=False, host='0.0.0.0')

    wsThread.wait()
