import datetime
import json
import os
from functools import wraps

from flask import Flask, render_template, jsonify, redirect, request, url_for, session
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask_socketio import SocketIO, emit
from flask_wtf import FlaskForm
from sqlalchemy.exc import OperationalError
from werkzeug.security import check_password_hash
from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length

from config import app_config
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
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(), Length(min=5, max=12, message=None)])
    password = StringField('password', validators=[DataRequired()])
    remember_me = BooleanField('remember_me')
    submit = SubmitField('Sign In')
    # recaptcha = RecaptchaField()

@app.errorhandler(404)
def page_not_found(e):
    return render_template('errorpages/404.html'), 404

@app.route('/login', methods=['GET', 'POST'])
def login():
    if (request.method == 'GET'):
#        username = Flask.request.values.get('user') # Your form's
#        password = Flask.request.values.get('pass') # input names
#        your_register_routine(username, password)
        return render_template("login.html", form=LoginForm())


    """For GET requests, display the login form. 
    For POSTS, login the current user by processing the form.

    """
    print(db)
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.get(form.username.data)
        if user:
            if check_password_hash(user.password, form.password.data):
                user.authenticated = True
                db.session.add(user)
                db.session.commit()
                login_user(user, remember=form.remember_me.data)
                return redirect(url_for('home'))
    return render_template("login.html", form=form, msg="Login failed")

def authenticated_resource(function):
    @wraps(function)
    def decorated(*args, **kwargs):
        if (session.get('authenticated')):
            return function(*args, **kwargs)
        if (current_user.is_authenticated):
            return function(*args, **kwargs)

        # return abort(403) # unauthenticated
        return redirect(url_for('login'))
    return decorated

@app.route("/logout", methods=["GET"])
@login_required
def logout():
    """Logout the current user."""
    user = current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    logout_user()
    return redirect(url_for('login'))


@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/usage")
@app.route("/usage/")
@app.route("/usage/<int:cnt>")
@authenticated_resource
def usage(cnt="undefined"):
    return render_template("usage_table.html", cnt=cnt)


@app.route("/usage_table")
@app.route("/usage_table/")
@app.route("/usage_table/<int:cnt>")
@authenticated_resource
def usage_table(cnt="undefined"):
    return render_template("usage_table.html", cnt=cnt)


@app.route("/usage_graph")
@app.route("/usage_graph/")
@app.route("/usage_graph/<int:cnt>")
@authenticated_resource
def usage_graph(cnt="undefined"):
    return render_template("usage_graph.html", cnt=cnt)


@app.route("/settings")
@app.route("/settings/")
@app.route("/settings/<int:active>")
@authenticated_resource
def settings(active=1):
    rPi = Raspberry()
    diag = Raspberry().get_all()
    diag_json = json.dumps(diag)
    return render_template("settings.html", active=active, diag=diag, diag_json=diag_json)


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

@app.route("/usage_data")
@app.route("/usage_data/")
@app.route("/usage_data/<int:cnt>")
def usage_data(cnt=100):
    device_measurement = EnergyDeviceMeasureModel()
    device_measurement.energy_device_id = "laadpaal_noord"
    qr = device_measurement.get_last_n_saved(energy_device_id="laadpaal_noord",n=cnt)
    qr_l = []
    for o in qr:
        qr_l.append(o.to_dict())  

    return jsonify(qr_l)

# Cnt is a maximum to limit impact of this request
@app.route("/usage_data_since/<path:since_timestamp>")
@app.route("/usage_data_since/<path:since_timestamp>/<int:cnt>")
def usage_data_since(since_timestamp, cnt=-1):
    device_measurement = EnergyDeviceMeasureModel()
    device_measurement.energy_device_id = "laadpaal_noord"
    qr = device_measurement.get_last_n_saved_since(energy_device_id="laadpaal_noord",since_ts=since_timestamp,n=cnt)
    qr_l = []
    for o in qr:
        qr_l.append(o.to_dict())  

    return jsonify(qr_l)

# Cnt is a maximum to limit impact of this request
@app.route("/charge_sessions")
@app.route("/charge_sessions/")
@app.route("/charge_sessions//<int:cnt>")
@app.route("/charge_sessions/<path:since_timestamp>")
@app.route("/charge_sessions/<path:since_timestamp>/<int:cnt>")
def charge_sessions(since_timestamp=None, cnt=-1):
    charge_sessions = SessionModel()
    charge_sessions.energy_device_id = "laadpaal_noord"
    qr = charge_sessions.get_last_n_sessions_since(energy_device_id="laadpaal_noord",since_ts=since_timestamp,n=cnt)
    qr_l = []
    for o in qr:
        qr_l.append(o.to_dict())

    return jsonify(qr_l)


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
