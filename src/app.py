from flask import Flask, render_template, jsonify, Response, redirect, request, url_for, session
from flask_socketio import SocketIO, emit
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import OperationalError
from functools import wraps
from config import app_config
from nl.carcharging.models import db
from nl.carcharging.views.SessionView import session_api as session_blueprint
from nl.carcharging.views.SessionView import scheduler
import os
from nl.carcharging.models.EnergyDeviceMeasureModel import EnergyDeviceMeasureModel
from nl.carcharging.services.EnergyUtil import EnergyUtil
import time
import datetime
import schedule
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length

# app initiliazation
app = Flask(__name__)

app.config.from_object(app_config[os.getenv('CARCHARGING_ENV')])
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# import os; os.urandom(24)
app.config['SECRET_KEY'] = '(*^&uytwejkfh8tsefukhg23eioHJYseryg(*^5eyt123eiuyowish))!'
app.config['WTF_CSRF_SECRET_KEY'] = 'iw(*&43^%$diuYGef9872(*&*&^*&triourv2r3iouh[p2ojdkjegqrfvuytf3eYTF]oiuhwOIU'

app.register_blueprint(session_blueprint, url_prefix='/api/v1/sessions')

socketio = SocketIO(app)

db.init_app(app)

# flask-login
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(db.Model):
    """
    """
    __tablename__ = 'users'

    username = db.Column(db.String, primary_key=True)
    password = db.Column(db.String)
    authenticated = db.Column(db.Boolean, default=False)

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.username

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False

class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(), Length(min=5, max=12, message=None)])
    password = StringField('password', validators=[DataRequired()])
    remember_me = BooleanField('remember_me')
    submit = SubmitField('Sign In')
    # recaptcha = RecaptchaField()


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

@app.route('/', methods=['GET'])
def index():
    return render_template("dashboard.html")

@app.route("/home")
@authenticated_resource
def home():
    return render_template("dashboard.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/usage")
@app.route("/usage/")
@app.route("/usage/<int:cnt>")
@authenticated_resource
#@login_required
def usage(cnt="undefined"):
#def usage():
    return render_template("usage.html", cnt=cnt)


@app.route("/usage_graph")
@app.route("/usage_graph/")
@app.route("/usage_graph/<int:cnt>")
@authenticated_resource
#@login_required
def usage_graph(cnt="undefined"):
#def usage():
    return render_template("usage_graph.html", cnt=cnt)


@app.route("/settings")
@app.route("/settings/")
@app.route("/settings/<int:active>")
@authenticated_resource
def settings(active=1):
#def usage():
    return render_template("settings.html", active=active)


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


class MapTool(object):
    counter = 1
    most_recent = ""

    def __init__(self):
        self.thread = None

    def start_server(self):
        print(f'{datetime.datetime.now()} - Starting websocket server...')
        socketio.run(app, port=5000, debug=True, use_reloader=False, host='0.0.0.0')

    def start(self):
        self.thread = socketio.start_background_task(self.start_server)

    def send_usage_update(self, type):
        print(f'{datetime.datetime.now()} - Checking usage data...')

        device_measurement = EnergyDeviceMeasureModel()  
        device_measurement.energy_device_id = "laadpaal_noord"
        qr = device_measurement.get_last_saved(energy_device_id="laadpaal_noord")
        if (self.most_recent != qr.get_created_at_str()):
            print(f'{datetime.datetime.now()} - Send msg {self.counter} via websocket...')
            socketio.emit('status_update', { 'data':  
                { "a_l1": qr.a_l1,
                   "a_l2": qr.a_l2,
                   "a_l3": qr.a_l3,
                   "created_at": qr.get_created_at_str(),
                   "energy_device_id": qr.energy_device_id,
                   "hz": qr.hz,
                   "kw_total": qr.kw_total,
                   "kwh_l1": qr.kwh_l1,
                   "kwh_l2": qr.kwh_l2,
                   "kwh_l3": qr.kwh_l3,
                   "p_l1": qr.p_l1,
                   "p_l2": qr.p_l2,
                   "p_l3": qr.p_l3,
                   "v_l1": qr.v_l1,
                   "v_l2": qr.v_l2,
                   "v_l3": qr.v_l3
                }}, 
                namespace='/usage'
            )
            self.most_recent = qr.get_created_at_str()
        else:
            print(f'{datetime.datetime.now()} - No change in usage at this time.')

        """
        now = datetime.datetime.now()
        # run this for each status update
        socketio.emit('status_update', { 'data':  
                { "a_l1": self.counter,
                   "a_l2": "15.9",
                   "a_l3": "16.0",
                   # "created_at": "01/01/2020, 16:38:11",
                   "created_at": now.strftime('%d/%m/%Y, %H:%M:%S'),
                   "energy_device_id": "laadpaal_noord",
                   "hz": "49.9",
                   "kw_total": "202.0",
                   "kwh_l1": "67.3",
                   "kwh_l2": "67.4",
                   "kwh_l3": "67.3",
                   "p_l1": "3697.3",
                   "p_l2": "3722.4",
                   "p_l3": "3737.7",
                   "v_l1": "230.6",
                   "v_l2": "233.5",
                   "v_l3": "233.1"
                }}, 
                namespace='/usage'
            )
        """
        self.counter += 1

    def wait(self):
        self.thread.join()


if __name__ == "__main__":
    maptool = MapTool()
    maptool.start()

    while True:
         socketio.sleep(7)
         try:
             maptool.send_usage_update("status_update")
         except OperationalError as e:
             # If the database is unavailable (or no access allowed), currently the entire app
             # crashes. Should remain running untill the access is restored!
             print(f'Something wrong with the database! {e}')

    maptool.wait()

#    socketio.run(app)
#socketio.run(app, host='localhost', port=5000)
#if __name__ == '__main__':
#    socketio.run(app, host='0.0.0.0')
