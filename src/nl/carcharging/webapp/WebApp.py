import datetime
import json
import os
from functools import wraps

from flask import Flask, render_template, jsonify, redirect, request, url_for, session
from flask_login import LoginManager
from flask_socketio import SocketIO, emit
from sqlalchemy.exc import OperationalError

from config import app_config, WebAppConfig
from nl.carcharging.models import db
from nl.carcharging.models.EnergyDeviceMeasureModel import EnergyDeviceMeasureModel
from nl.carcharging.models.Raspberry import Raspberry
from nl.carcharging.models.SessionModel import SessionModel
from nl.carcharging.models.User import User
from nl.carcharging.views.SessionView import session_api as session_blueprint

from nl.carcharging.webapp.routes import webapp

#import routes

# app initiliazation
app = Flask(__name__)


app.config.from_object(app_config[os.getenv('CARCHARGING_ENV')])
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# import os; os.urandom(24)
app.config['SECRET_KEY'] = '(*^&uytwejkfh8tsefukhg23eioHJYseryg(*^5eyt123eiuyowish))!'
app.config['WTF_CSRF_SECRET_KEY'] = 'iw(*&43^%$diuYGef9872(*&*&^*&triourv2r3iouh[p2ojdkjegqrfvuytf3eYTF]oiuhwOIU'

app.register_blueprint(session_blueprint, url_prefix='/api/v1/sessions')
# The CarCharger root webapp
app.register_blueprint(webapp) # no url_prefix

socketio = SocketIO(app)
#socketio = SocketIO(app, async_mode=async_mode)

db.init_app(app)

# flask-login
WebAppConfig.login_manager = LoginManager()
WebAppConfig.login_manager.init_app(app)

@WebAppConfig.login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@socketio.on("connect", namespace="/usage")
def connect():
    emit("server_status", "server_up")
    print("Client connected...")

@socketio.on("disconnect", namespace="/usage")
def disconnect():
    print('Client disconnected.')

# This event currently is not used, just for reference
@socketio.on('my event', namespace='/usage')
def handle_usage_event(json):
    print('received json: ' + str(json))
    return ( 'one', 2 )    # client callback


@app.errorhandler(404)
def page_not_found(e):
    return render_template('errorpages/404.html'), 404



class WebApp(object):
    # Count the message updates send through the websocket
    counter = 1
    most_recent = ""

    def __init__(self):
        self.thread = None

    def start_server(self):
        print(f'{datetime.datetime.now()} - Starting web server in separate thread...')
        socketio.run(app, port=5000, debug=True, use_reloader=False, host='0.0.0.0')

    def websocket_start(self):
        print(f'{datetime.datetime.now()} - Starting background task...')
        while True:
            socketio.sleep(7)
            try:
                webapp.websocket_send_usage_update("status_update")
            except OperationalError as e:
                # If the database is unavailable (or no access allowed),
                # remain running untill the access is restored
                print(f'Something wrong with the database! {e}')

    def start(self):
        print(f'{datetime.datetime.now()} - Launching background task...')
        self.thread = socketio.start_background_task(self.websocket_start)

    def websocket_send_usage_update(self, type):
        print(f'{datetime.datetime.now()} - Checking usage data...')

        device_measurement = EnergyDeviceMeasureModel()  
        device_measurement.energy_device_id = "laadpaal_noord"
        qr = device_measurement.get_last_saved(energy_device_id="laadpaal_noord")
        if (self.most_recent != qr.get_created_at_str()):
            print(f'{datetime.datetime.now()} - Send msg {self.counter} via websocket...')
            socketio.emit('status_update', { 'data': qr.to_str() }, namespace='/usage')
            self.most_recent = qr.get_created_at_str()
        else:
            print(f'{datetime.datetime.now()} - No change in usage at this time.')

        self.counter += 1

    def wait(self):
        self.thread.join()


if __name__ == "__main__":
    webapp = WebApp()
    webapp.start()

    print(f'{datetime.datetime.now()} - Starting web server...')
    socketio.run(app, port=5000, debug=True, use_reloader=False, host='0.0.0.0')

    webapp.wait()
