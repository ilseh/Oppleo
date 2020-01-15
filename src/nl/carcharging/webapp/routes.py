from flask import Blueprint, render_template, abort, request, url_for, redirect, jsonify, session

from jinja2.exceptions import TemplateNotFound
from werkzeug.security import check_password_hash
from functools import wraps
import json

from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask_socketio import SocketIO, emit

from nl.carcharging.models import db
from nl.carcharging.models.User import User
from nl.carcharging.webapp.LoginForm import LoginForm
from nl.carcharging.models.EnergyDeviceMeasureModel import EnergyDeviceMeasureModel
from nl.carcharging.models.Raspberry import Raspberry
from nl.carcharging.models.SessionModel import SessionModel



""" 
 - make sure all url_for routes point to this blueprint
"""
webapp = Blueprint('webapp', __name__, template_folder='templates')

@webapp.route('/', methods=['GET'])
def index():
    try:
        return render_template('dashboard.html')
    except TemplateNotFound:
        abort(404)

@webapp.route("/home")
#@authenticated_resource
def home():
    try:
        return render_template('dashboard.html')
    except TemplateNotFound:
        abort(404)


@webapp.errorhandler(404)
def page_not_found(e):
    return render_template('errorpages/404.html'), 404

@webapp.route('/login', methods=['GET', 'POST'])
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
                return redirect(url_for('webapp.home'))
    return render_template("login.html", form=form, msg="Login failed")

def authenticated_resource(function):
    @wraps(function)
    def decorated(*args, **kwargs):
        if (session.get('authenticated')):
            return function(*args, **kwargs)
        if (current_user.is_authenticated):
            return function(*args, **kwargs)

        # return abort(403) # unauthenticated
        return redirect(url_for('webapp.login'))
    return decorated

@webapp.route("/logout", methods=["GET"])
@login_required
def logout():
    """Logout the current user."""
    user = current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    logout_user()
    return redirect(url_for('webapp.login'))


@webapp.route("/about")
def about():
    return render_template("about.html")

@webapp.route("/usage")
@webapp.route("/usage/")
@webapp.route("/usage/<int:cnt>")
@authenticated_resource
def usage(cnt="undefined"):
    return render_template("usage_table.html", cnt=cnt)


@webapp.route("/usage_table")
@webapp.route("/usage_table/")
@webapp.route("/usage_table/<int:cnt>")
@authenticated_resource
def usage_table(cnt="undefined"):
    return render_template("usage_table.html", cnt=cnt)


@webapp.route("/usage_graph")
@webapp.route("/usage_graph/")
@webapp.route("/usage_graph/<int:cnt>")
@authenticated_resource
def usage_graph(cnt="undefined"):
    return render_template("usage_graph.html", cnt=cnt)


@webapp.route("/settings")
@webapp.route("/settings/")
@webapp.route("/settings/<int:active>")
@authenticated_resource
def settings(active=1):
    diag = Raspberry().get_all()
    diag_json = json.dumps(diag)
    return render_template("settings.html", active=active, diag=diag, diag_json=diag_json)


@webapp.route("/usage_data")
@webapp.route("/usage_data/")
@webapp.route("/usage_data/<int:cnt>")
def usage_data(cnt=100):
    device_measurement = EnergyDeviceMeasureModel()
    device_measurement.energy_device_id = "laadpaal_noord"
    qr = device_measurement.get_last_n_saved(energy_device_id="laadpaal_noord",n=cnt)
    qr_l = []
    for o in qr:
        qr_l.append(o.to_dict())  

    return jsonify(qr_l)

# Cnt is a maximum to limit impact of this request
@webapp.route("/usage_data_since/<path:since_timestamp>")
@webapp.route("/usage_data_since/<path:since_timestamp>/<int:cnt>")
def usage_data_since(since_timestamp, cnt=-1):
    device_measurement = EnergyDeviceMeasureModel()
    device_measurement.energy_device_id = "laadpaal_noord"
    qr = device_measurement.get_last_n_saved_since(energy_device_id="laadpaal_noord",since_ts=since_timestamp,n=cnt)
    qr_l = []
    for o in qr:
        qr_l.append(o.to_dict())  

    return jsonify(qr_l)

# Cnt is a maximum to limit impact of this request
@webapp.route("/charge_sessions")
@webapp.route("/charge_sessions/")
@webapp.route("/charge_sessions//<int:cnt>")
@webapp.route("/charge_sessions/<path:since_timestamp>")
@webapp.route("/charge_sessions/<path:since_timestamp>/<int:cnt>")
def charge_sessions(since_timestamp=None, cnt=-1):
    charge_sessions = SessionModel()
    charge_sessions.energy_device_id = "laadpaal_noord"
    qr = charge_sessions.get_last_n_sessions_since(energy_device_id="laadpaal_noord",since_ts=since_timestamp,n=cnt)
    qr_l = []
    for o in qr:
        qr_l.append(o.to_dict())

    return jsonify(qr_l)