from flask import Flask, Blueprint, render_template, abort, request, url_for, redirect, jsonify, session

from flask import current_app as app # Note: that the current_app proxy is only available in the context of a request.

from jinja2.exceptions import TemplateNotFound
from werkzeug.security import generate_password_hash, check_password_hash

from functools import wraps
import json

from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask_socketio import SocketIO, emit

from config import app_config, WebAppConfig

from nl.carcharging.models import db
from nl.carcharging.models.User import User
from nl.carcharging.webapp.LoginForm import LoginForm
from nl.carcharging.models.EnergyDeviceMeasureModel import EnergyDeviceMeasureModel
from nl.carcharging.models.Raspberry import Raspberry
from nl.carcharging.models.ChargeSessionModel import ChargeSessionModel
from nl.carcharging.models.RfidModel import RfidModel
from nl.carcharging.models.ChargerConfigModel import ChargerConfigModel
from nl.carcharging.webapp.ChangePasswordForm import ChangePasswordForm
from nl.carcharging.webapp.RfidChangeForm import RfidChangeForm
from nl.carcharging.api.TeslaApi import TeslaAPI


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
    return redirect('/')


@webapp.errorhandler(404)
def page_not_found(e):
    return render_template('errorpages/404.html'), 404

@webapp.route('/login', methods=['GET', 'POST'])
def login():
    # For GET requests, display the login form. 
    if (request.method == 'GET'):
#        username = Flask.request.values.get('user') # Your form's
#        password = Flask.request.values.get('pass') # input names
#        your_register_routine(username, password)
        return render_template("login.html", form=LoginForm())
    # For POST requests, login the current user by processing the form.
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
                if 'login_next' in session:
                    login_next = session['login_next']
                    del session['login_next']
                    return redirect(login_next)
                else:
                    # Return to the home page
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
        # Not allowed.
        # delete old - never used - cookie
        if 'login_next' in session:
            del session['login_next']
        # if somehow ended up at logout, don't forward to login
        if (request.endpoint == "webapp.logout"):
            return redirect(url_for('webapp.home'))
        # Redirect to login but rememmber the original request 
        session['login_next'] = request.full_path
        return redirect(url_for('webapp.login'))
    return decorated

@webapp.route("/logout", methods=["GET"])
@authenticated_resource
#@login_required
def logout():
    """Logout the current user."""
    user = current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    logout_user()
    # return redirect(url_for('webapp.login'))
    return redirect(url_for('webapp.home'))


@webapp.route("/change_password", methods=["GET", "POST"])
@authenticated_resource
def change_password():
    if (request.method == 'GET'):
        return render_template(
            'change_password.html', 
            form=ChangePasswordForm()
            )

    form = ChangePasswordForm()
    # Validate current password
    if not check_password_hash(current_user.password, form.current_password.data):
        # Current password correct
        form.current_password.errors = []
        form.current_password.errors.append('Het huidige admin wachtwoord is niet juist.')
        return render_template(
            'change_password.html', 
            form=form
            )
    if form.validate_on_submit():
        # Valid, change the password for the user now
        user = current_user
        user.password=generate_password_hash(form.new_password.data)
        db.session.add(user)
        db.session.commit()
        return render_template(
            'change_password_success.html', 
            )
    # Translate errors
    if ('new_password' in form.errors):
        for i in range(len(form.errors['new_password'])):
            if form.errors['new_password'][i] == "Field must be between 8 and 25 characters long.":
                form.errors['new_password'][i] = "Wachtwoord moet tussen 8 en 25 karakters lang zijn."
    if ('confirm_password' in form.errors):
        for i in range(len(form.errors['confirm_password'])):
            if form.errors['confirm_password'][i] == "Passwords must match":
                form.errors['confirm_password'][i] = "Wachtwoord moet gelijk zijn aan het wachtwoord hierboven."
    if ('csrf_token' in form.errors):
        for i in range(len(form.errors['csrf_token'])):
            if form.errors['csrf_token'][i] == "The CSRF token is invalid.":
                form.errors['csrf_token'][i] = "Het CSRF token is verlopen. Herlaad de pagina om een nieuw token te genereren."

    # Not valid - error message
    return render_template(
        'change_password.html', 
        form=form
        )


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
    charger_config_str = ChargerConfigModel().get_config()[0].to_str()
    return render_template("settings.html", 
                active=active, 
                diag=diag, 
                diag_json=diag_json, 
                charger_config=charger_config_str
            )


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
@webapp.route("/charge_sessions//")
@webapp.route("/charge_sessions///")
@webapp.route("/charge_sessions/<path:since_timestamp>")
@webapp.route("/charge_sessions/<path:since_timestamp>/")
@webapp.route("/charge_sessions/<path:since_timestamp>//")
@webapp.route("/charge_sessions/<path:since_timestamp>/<int:cnt>")
@webapp.route("/charge_sessions/<path:since_timestamp>/<int:cnt>/")
@webapp.route("/charge_sessions//<int:cnt>")
@webapp.route("/charge_sessions//<int:cnt>/")
@webapp.route("/charge_sessions///<path:format>")
@webapp.route("/charge_sessions/<path:since_timestamp>//<path:format>")
@webapp.route("/charge_sessions/<path:since_timestamp>/<int:cnt>/<path:format>")
@webapp.route("/charge_sessions//<int:cnt>/<path:format>")
def charge_sessions(since_timestamp=None, cnt=-1, format='html'):
    if (format.strip().lower() != 'json'):
        return render_template("charge_sessions.html")
    charge_sessions = ChargeSessionModel()
    charge_sessions.energy_device_id = "laadpaal_noord"
    qr = charge_sessions.get_last_n_sessions_since(energy_device_id="laadpaal_noord",since_ts=since_timestamp,n=cnt)
    qr_l = []
    for o in qr:
        qr_l.append(o.to_dict())
    return jsonify(qr_l)


# Cnt is a maximum to limit impact of this request
@webapp.route("/rfid_tokens", methods=["GET"])
@webapp.route("/rfid_tokens/", methods=["GET"])
@webapp.route("/rfid_tokens//", methods=["GET"])
@webapp.route("/rfid_tokens//<path:format>", methods=["GET"])
@webapp.route("/rfid_tokens/<path:token>/", methods=["GET", "POST"])
@webapp.route("/rfid_tokens/<path:token>/<path:format>", methods=["GET"])
@authenticated_resource
def rfid_tokens(format='html', token=None):
    if (format.strip().lower() != 'json'):
        if (token == None):
            return render_template("tokens.html")
        rfid_model = RfidModel().get_one(token)
        if (rfid_model == None):
            return render_template("tokens.html")
        rfid_change_form = RfidChangeForm()
        print('CSRF Token: {}'.format(rfid_change_form.csrf_token.current_token) )
        if (request.method == 'POST'):
            # Update for specific token
            if rfid_change_form.validate_on_submit():
                # TODO apply changes
                pass
            return render_template("token.html",
                    rfid_model=rfid_model,
                    form=rfid_change_form
                )        
        return render_template("token.html",
                    rfid_model=rfid_model,
                    form=rfid_change_form
                )        
    # Check if token exist, if not rfid is None
    rfid_list = []
    rfid_model = RfidModel().get_one(token)
    if ((token == None) or (rfid_model == None)):
        rfid_models = RfidModel().get_all()
        for rfid_model in rfid_models:
            rfid_list.append(rfid_model.to_str())
    return jsonify(rfid_list)


@webapp.route("/rfid_tokens/<path:token>/TeslaAPI/GenerateOAuth/json", methods=["POST"])
@authenticated_resource
def TeslaApi_GenerateOAuth(token=None):
    rfid_model = RfidModel().get_one(token)
    rfid_change_form = RfidChangeForm()

    c1 = request.form['csrf_token']
    c2 = rfid_change_form.csrf_token.current_token
    c3 = (c1 == c2)

    if ('csrf_token' not in request.form) or \
       (request.form['csrf_token'] != rfid_change_form.csrf_token.current_token):
        return jsonify({
            'status': 'failed', 
            'reason': 'Invalid csrf_token'
            })
    # Update for specific token
    tesla_api = TeslaApi()
    if tesla_api.authenticate(
        username=request['form']['oauth_email'], 
        password=request['form']['oauth_password']):
        rfid_model.api_access_token  = tesla_api.access_token        
        rfid_model.api_token_type    = tesla_api.token_type        
        rfid_model.api_created_at    = tesla_api.created_at        
        rfid_model.api_expires_in    = tesla_api.expires_in        
        rfid_model.api_refresh_token = tesla_api.refresh_token        
        # Obtained token
        return jsonify({
            'status': 'success', 
            'token_type': tesla_api.token_type, 
            'created_at': tesla_api.created_at, 
            'expires_in': tesla_api.expires_in
            })
    else:
        # Nope, no token
        return jsonify({
            'status': 'failed', 
            'reason': 'Not authorized'
            })


@webapp.route("/rfid_tokens/<path:token>/TeslaAPI/RefreshOAuth", methods=["GET"])
@authenticated_resource
def TeslaApi_RefreshOAuth(token=None):
    pass