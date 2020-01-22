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
from nl.carcharging.utils.UpdateOdometerTeslaUtil import UpdateOdometerTeslaUtil
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
        rfid_model.cleanupOldToken()    # Remove any expired token info
        rfid_change_form = RfidChangeForm()
        print('CSRF Token: {}'.format(rfid_change_form.csrf_token.current_token) )
        if (request.method == 'POST'):
            # Update for specific token
            if rfid_change_form.validate_on_submit():
                # rfid - given
                rfid_model.enabled = rfid_change_form.enabled.data
                # created_at - updated by the system
                # last_used_at - updated by the system
                rfid_model.name = rfid_change_form.name.data
                rfid_model.vehicle_make = rfid_change_form.vehicle_make.data
                rfid_model.vehicle_model = rfid_change_form.vehicle_model.data
                # only accept odometer if token and id
                rfid_model.get_odometer = (rfid_change_form.get_odometer.data and 
                                           rfid_model.hasValidToken() and 
                                           rfid_change_form.vehicle_id.data is not None and
                                           len(rfid_change_form.vehicle_id.data) > 0)
                rfid_model.license_plate = rfid_change_form.license_plate.data
                rfid_model.valid_from = rfid_change_form.valid_from.data
                rfid_model.valid_until = rfid_change_form.valid_until.data
                # api_access_token - updated via ajax
                # api_token_type - updated via ajax
                # api_created_at - updated via ajax
                # api_expires_in - updated via ajax
                # api_refresh_token - updated via ajax
                rfid_model.vehicle_name = None if rfid_change_form.vehicle_name.data is None or \
                                                  len(rfid_change_form.vehicle_name.data) == 0 \
                                               else rfid_change_form.vehicle_name.data
                rfid_model.vehicle_id = None if rfid_change_form.vehicle_id.data is None or \
                                                len(rfid_change_form.vehicle_id.data) == 0 \
                                             else rfid_change_form.vehicle_id.data
                rfid_model.vehicle_vin = None if rfid_change_form.vehicle_vin.data is None or \
                                                 len(rfid_change_form.vehicle_vin.data) == 0 \
                                              else rfid_change_form.vehicle_vin.data
                rfid_model.save()

                # Return to the rfid tokens page
                return redirect(url_for('webapp.rfid_tokens', format='html', token=None))

            # TODO - what went wrong? message!
            return render_template("token.html",
                    rfid_model=rfid_model,
                    form=rfid_change_form
                )        
        return render_template("token.html",
                    rfid_model=rfid_model,
                    form=rfid_change_form
                )        
    # Check if token exist, if not rfid is None
    if (token == None):
        rfid_list = []
        rfid_models = RfidModel().get_all()
        for rfid_model in rfid_models:
            rfid_model.cleanupOldToken()    # Remove any expired token info
            rfid_list.append(rfid_model.to_str())
        return jsonify(rfid_list)
    # Specific token
    rfid_model = RfidModel().get_one(token)
    if (rfid_model == None):
        return jsonify({})
    rfid_model.cleanupOldToken()    # Remove any expired token info
    return jsonify(rfid_model.to_str())


@webapp.route("/rfid_tokens/<path:token>/TeslaAPI/GenerateOAuth/json", methods=["POST"])
@authenticated_resource
def TeslaApi_GenerateOAuth(token=None):
    # CSRF Token is valid
    rfid_model = RfidModel().get_one(token)
    if ((token == None) or (rfid_model == None)):
        # Nope, no token
        return jsonify({
            'status': 404, 
            'reason': 'No known RFID token'
            })

    # Update for specific token
    tesla_api = TeslaAPI()
    if tesla_api.authenticate(
        email=request.form['oauth_email'], 
        password=request.form['oauth_password']):
        # Obtained token
        UpdateOdometerTeslaUtil.copy_token_from_api_to_rfid_model(tesla_api, rfid_model)
        rfid_model.save()
        return jsonify({
            'status': 200, 
            'token_type': rfid_model.api_token_type, 
            'created_at': rfid_model.api_created_at, 
            'expires_in': rfid_model.api_expires_in,
            'vehicles' : tesla_api.getVehicleNameIdList()
            })
    else:
        # Nope, no token
        return jsonify({
            'status': 401,  
            'reason': 'Not authorized'
            })


@webapp.route("/rfid_tokens/<path:token>/TeslaAPI/RefreshOAuth/json", methods=["POST"])
@authenticated_resource
def TeslaApi_RefreshOAuth(token=None):
    # CSRF Token is valid
    rfid_model = RfidModel().get_one(token)
    if ((token == None) or (rfid_model == None)):
        # Nope, no token
        return jsonify({
            'status': 404, 
            'reason': 'No known RFID token'
            })
    # Update for specific token
    tesla_api = TeslaAPI()
    UpdateOdometerTeslaUtil.copy_token_from_rfid_model_to_api(rfid_model, tesla_api)
    if not tesla_api.refreshToken():
        return jsonify({
            'status': 500,
            'reason': 'Refresh failed'
            })
    # Refresh succeeded, Obtained token
    UpdateOdometerTeslaUtil.copy_token_from_api_to_rfid_model(tesla_api, rfid_model)
    rfid_model.save()

    return jsonify({
        'status': 200, 
        'token_type': rfid_model.api_token_type, 
        'created_at': rfid_model.api_created_at, 
        'expires_in': rfid_model.api_expires_in,
        'vehicles' : tesla_api.getVehicleNameIdList()
        })

@webapp.route("/rfid_tokens/<path:token>/TeslaAPI/RevokeOAuth/json", methods=["POST"])
@authenticated_resource
def TeslaApi_RevokeOAuth(token=None):
    # CSRF Token is valid
    rfid_model = RfidModel().get_one(token)
    if ((token == None) or (rfid_model == None)):
        # Nope, no token
        return jsonify({
            'status': 404, 
            'reason': 'No known RFID token'
            })
    # Update for specific token
    tesla_api = TeslaAPI()
    UpdateOdometerTeslaUtil.copy_token_from_rfid_model_to_api(rfid_model, tesla_api)
    if not tesla_api.revokeToken():
        return jsonify({
            'status': 500,
            'reason': 'Revoke failed'
            })
    # Revoke succeeded, remove token
    UpdateOdometerTeslaUtil.clean_token_rfid_model(rfid_model)
    rfid_model.save()

    return jsonify({
        'status': 200, 
        'token_type': '', 
        'created_at': '', 
        'expires_in': '',
        'vehicles' : ''
        })
