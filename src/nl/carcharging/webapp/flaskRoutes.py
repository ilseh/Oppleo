import os
import threading
from flask import Flask, Blueprint, render_template, abort, request, url_for, redirect, jsonify, session

from flask import current_app as app # Note: that the current_app proxy is only available in the context of a request.

from jinja2.exceptions import TemplateNotFound
from werkzeug.security import generate_password_hash, check_password_hash

from functools import wraps
import json
import logging
from urllib.parse import urlparse

from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask_socketio import SocketIO, emit

from nl.carcharging.config.WebAppConfig import WebAppConfig

from nl.carcharging.models.User import User
from nl.carcharging.webapp.LoginForm import LoginForm
from nl.carcharging.webapp.AuthorizeForm import AuthorizeForm
from nl.carcharging.models.EnergyDeviceMeasureModel import EnergyDeviceMeasureModel
from nl.carcharging.models.Raspberry import Raspberry
from nl.carcharging.models.ChargeSessionModel import ChargeSessionModel
from nl.carcharging.models.RfidModel import RfidModel
from nl.carcharging.models.ChargerConfigModel import ChargerConfigModel
from nl.carcharging.models.EnergyDeviceModel import EnergyDeviceModel
from nl.carcharging.models.OffPeakHoursModel import OffPeakHoursModel
from nl.carcharging.webapp.ChangePasswordForm import ChangePasswordForm
from nl.carcharging.webapp.RfidChangeForm import RfidChangeForm
from nl.carcharging.api.TeslaApi import TeslaAPI
from nl.carcharging.utils.UpdateOdometerTeslaUtil import UpdateOdometerTeslaUtil
from nl.carcharging.services.Evse import Evse
from nl.carcharging.services.EvseReaderProd import EvseState
from nl.carcharging.utils.WebSocketUtil import WebSocketUtil

""" 
 - make sure all url_for routes point to this blueprint
"""
flaskRoutes = Blueprint('flaskRoutes', __name__, template_folder='templates')

flaskRoutesLogger = logging.getLogger('nl.carcharging.webapp.flaskRoutes')
flaskRoutesLogger.debug('Initializing routes')

threadLock = threading.Lock()


@flaskRoutes.route('/', methods=['GET'])
def index():
    global flaskRoutesLogger, WebAppConfig
    flaskRoutesLogger.debug('/ {}'.format(request.method))
    try:
        return render_template(
            'dashboard.html',
            webappconfig=WebAppConfig
            )
    except TemplateNotFound:
        abort(404)
    except Exception as e:
        flaskRoutesLogger.debug('/  - exception')
        flaskRoutesLogger.debug(e)

@flaskRoutes.route("/home")
#@authenticated_resource
def home():
    global flaskRoutesLogger
    flaskRoutesLogger.debug('/home {}'.format(request.method))
    return redirect('/')


@flaskRoutes.errorhandler(404)
def page_not_found(e):
    global flaskRoutesLogger
    flaskRoutesLogger.debug('404 page not found error handler')
    # No need for webappconfig=WebAppConfig
    return render_template('errorpages/404.html'), 404


@flaskRoutes.route('/login', methods=['GET', 'POST'])
def login():
    # For GET requests, display the login form. 
    global flaskRoutesLogger, WebAppConfig
    flaskRoutesLogger.debug('/login {}'.format(request.method))
    if (request.method == 'GET'):
        return render_template("login.html", 
            form=LoginForm(),
            webappconfig=WebAppConfig
            )
    # For POST requests, login the current user by processing the form.
    form = LoginForm()
    flaskRoutesLogger.debug('login form created')
    if form.validate_on_submit():
        flaskRoutesLogger.debug('loginForm valid on submit')
        user = User.get(form.username.data)
        flaskRoutesLogger.debug('loginForm valid on submit')
        try:
            flaskRoutesLogger.debug('form.username.data = ' + form.username.data)
            if user is not None:
                flaskRoutesLogger.debug('if user:')
                if check_password_hash(user.password, form.password.data):
                    flaskRoutesLogger.debug('check_password_hash ok, login_user()')
                    login_user(user, remember=form.remember_me.data)
                    user.authenticated = True
                    user.save()
                    if 'login_next' in session:
                        flaskRoutesLogger.debug('login_next: %s' % session['login_next'])
                        login_next = session['login_next']
                        del session['login_next']
                        # only allow relative paths, so there cannot be a netloc (host)
                        if bool(urlparse(login_next).netloc):
                            # do not allow this 
                            flaskRoutesLogger.debug('login_next: {} not allowed. Using default route'.format(login_next))
                            return redirect(url_for('flaskRoutes.home'))
                        # Safe next
                        return redirect(login_next)
                    else:
                        # Return to the home page
                        flaskRoutesLogger.debug('flaskRoutes.home')
                        return redirect(url_for('flaskRoutes.home'))
        except Exception as e:
            flaskRoutesLogger.debug(type(e))
            flaskRoutesLogger.debug(e.args)
            flaskRoutesLogger.debug(e)


    flaskRoutesLogger.debug('nothing of that all')
    return render_template("login.html", 
                form=form, 
                msg="Login failed",
                webappconfig=WebAppConfig
                )

def authenticated_resource(function):
    @wraps(function)
    def decorated(*args, **kwargs):
        if (current_user.is_authenticated):
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
    return decorated

@flaskRoutes.route("/logout", methods=["GET"])
@authenticated_resource
#@login_required
def logout():
    global flaskRoutesLogger
    flaskRoutesLogger.debug('/logout {}'.format(request.method))
    # Logout the current user
    user = current_user
    user.authenticated = False
    user.save()
    logout_user()
    return redirect(url_for('flaskRoutes.home'))


@flaskRoutes.route("/change_password", methods=["GET", "POST"])
@authenticated_resource
def change_password():
    global flaskRoutesLogger, WebAppConfig
    flaskRoutesLogger.debug('/change_password {}'.format(request.method))
    if (request.method == 'GET'):
        return render_template(
            'change_password.html', 
            form=ChangePasswordForm(),
            webappconfig=WebAppConfig
            )

    form = ChangePasswordForm()
    # Validate current password
    if not check_password_hash(current_user.password, form.current_password.data):
        # Current password correct
        form.current_password.errors = []
        form.current_password.errors.append('Het huidige admin wachtwoord is niet juist.')
        return render_template(
            'change_password.html', 
            form=form,
            webappconfig=WebAppConfig
            )
    if form.validate_on_submit():
        # Valid, change the password for the user now
        user = current_user
        user.password = generate_password_hash(form.new_password.data)
        user.save()
        return render_template(
            'change_password_success.html', 
            webappconfig=WebAppConfig
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
        form=form,
        webappconfig=WebAppConfig
        )


@flaskRoutes.route("/about")
def about():
    global flaskRoutesLogger, WebAppConfig
    flaskRoutesLogger.debug('/about {}'.format(request.method))
    return render_template("about.html",
                webappconfig=WebAppConfig
                )


@flaskRoutes.route("/shutdown", methods=["GET", "POST"])
@flaskRoutes.route("/shutdown/", methods=["GET", "POST"])
@authenticated_resource
def shutdown():
    global flaskRoutesLogger, WebAppConfig
    # For GET requests, display the authorize form. 
    flaskRoutesLogger.debug('/shutdown {}'.format(request.method))
    if (request.method == 'GET'):
        return render_template("authorize.html", 
            form=AuthorizeForm(),
            requesttitle="Uitschakelen",
            buttontitle="Schakel uit!",
            webappconfig=WebAppConfig
            )
    # For POST requests, login the current user by processing the form.
    form = AuthorizeForm()
    if form.validate_on_submit() and \
       check_password_hash(current_user.password, form.password.data):
        flaskRoutesLogger.debug('Shutdown requested and authorized. Shutting down in 2 seconds...')
        # Simple os.system('sudo shutdown now') initiates shutdown before a webpage can be returned
        os.system("nohup sudo -b bash -c 'sleep 2; shutdown now' &>/dev/null")
        return render_template("shuttingdown.html", 
                    webappconfig=WebAppConfig
                    )
    else:
        return render_template("authorize.html", 
                form=form, 
                requesttitle="Uitschakelen",
                buttontitle="Schakel uit!",
                errormsg="Het wachtwoord is onjuist",
                webappconfig=WebAppConfig
                )


@flaskRoutes.route("/reboot", methods=["GET", "POST"])
@flaskRoutes.route("/reboot/", methods=["GET", "POST"])
@authenticated_resource
def reboot():
    global flaskRoutesLogger, WebAppConfig
    # For GET requests, display the authorize form. 
    flaskRoutesLogger.debug('/reboot {}'.format(request.method))
    if (request.method == 'GET'):
        return render_template("authorize.html", 
            form=AuthorizeForm(),
            requesttitle="Herstarten",
            buttontitle="Herstart!",
            webappconfig=WebAppConfig
            )
    # For POST requests, login the current user by processing the form.
    form = AuthorizeForm()
    if form.validate_on_submit() and \
       check_password_hash(current_user.password, form.password.data):
        flaskRoutesLogger.debug('Reboot requested and authorized. Rebooting in 2 seconds...')
        # Simple os.system('sudo reboot') initiates reboot before a webpage can be returned
        os.system("nohup sudo -b bash -c 'sleep 2; reboot' &>/dev/null")
        return render_template("rebooting.html", 
                    webappconfig=WebAppConfig
                    )
    else:
        return render_template("authorize.html", 
                form=form, 
                requesttitle="Herstarten",
                buttontitle="Herstart!",
                errormsg="Het wachtwoord is onjuist",
                webappconfig=WebAppConfig
                )



@flaskRoutes.route("/delete_charge_session/<int:id>", methods=["GET", "POST"])
@authenticated_resource
def delete_charge_session(id=None):
    global flaskRoutesLogger, WebAppConfig
    if id is None:
        return jsonify({
            'status': 404, 
            'id': WebAppConfig.ENERGY_DEVICE_ID, 
            'reason': 'Laadsessie niet gevonden'
            })
    # For GET requests, display the authorize form. 
    flaskRoutesLogger.debug('/delete_charge_session {}'.format(request.method))
    if (request.method == 'GET'):
        return render_template("authorize.html", 
            form=AuthorizeForm(),
            requesttitle=str("Laadsessie " + str(id)),
            buttontitle=str("Verwijder laadsessie " + str(id)),
            webappconfig=WebAppConfig
            )
    # For POST requests, login the current user by processing the form.
    form = AuthorizeForm()
    if form.validate_on_submit() and \
       check_password_hash(current_user.password, form.password.data):
        flaskRoutesLogger.debug('delete_charge_session requested and authorized.')
        charge_session = ChargeSessionModel.get_one_charge_session(id)
        charge_session.delete()
        return redirect(url_for('flaskRoutes.charge_sessions'))
    else:
        return render_template("authorize.html", 
                form=form, 
                requesttitle=str("Laadsessie " + str(id)),
                buttontitle=str("Verwijder laadsessie " + str(id)),
                errormsg="Het wachtwoord is onjuist",
                webappconfig=WebAppConfig
                )


@flaskRoutes.route("/start_charge_session/<int:rfid>", methods=["GET", "POST"])
@authenticated_resource
def start_charge_session(rfid=None):
    global flaskRoutesLogger, WebAppConfig, threadLock
    if rfid is None:
        return jsonify({
            'status': 404, 
            'id': WebAppConfig.ENERGY_DEVICE_ID, 
            'reason': 'RFID niet gevonden'
            })
    # For GET requests, display the authorize form. 
    flaskRoutesLogger.debug('/start_charge_session {}'.format(request.method))
    if (request.method == 'GET'):
        return render_template("authorize.html", 
            form=AuthorizeForm(),
            requesttitle=str("Start laadsessie"),
            buttontitle="Start laadsessie",
            webappconfig=WebAppConfig
            )
    # For POST requests, login the current user by processing the form.
    form = AuthorizeForm()
    if form.validate_on_submit() and \
       check_password_hash(current_user.password, form.password.data):
        flaskRoutesLogger.debug('start_charge_session requested and authorized.')
        with threadLock:

            charge_session = ChargeSessionModel.get_open_charge_session_for_device(WebAppConfig.ENERGY_DEVICE_ID)
            if charge_session is None:
                try:
                    WebAppConfig.chThread.authorize(rfid)
                    WebAppConfig.chThread.start_charge_session(
                                    rfid=rfid,
                                    trigger=ChargeSessionModel.TRIGGER_WEB,
                                    condense=False
                                )
                    WebAppConfig.chThread.buzz_ok()
                    WebAppConfig.chThread.update_charger_and_led(True)
                except NotAuthorizedException as e:
                    flaskRoutesLogger.warn('Could not start charge session for rfid {}, NotAuthorized!'.format(id))
                    return render_template("authorize.html", 
                            form=form, 
                            requesttitle=str("Start laadsessie " + str(id)),
                            buttontitle="Start laadsessie",
                            errormsg="Deze RFID is niet geautoriseerd.",
                            webappconfig=WebAppConfig
                            )
                except ExpiredException as e:
                    flaskRoutesLogger.warn('Could not start charge session for rfid {}, Expired!'.format(id))
                    return render_template("authorize.html", 
                            form=form, 
                            requesttitle=str("Start laadsessie " + str(id)),
                            buttontitle="Start laadsessie",
                            errormsg="De geldigheid van deze RFID is verlopen.",
                            webappconfig=WebAppConfig
                            )
            else:
                # A charge session was started elsewhere, fail
                flaskRoutesLogger.warn('Could not start charge session for rfid {}, already session active!'.format(id))
                return render_template("authorize.html", 
                        form=form, 
                        requesttitle=str("Start laadsessie " + str(id)),
                        buttontitle="Start laadsessie",
                        errormsg="Er is al een laadsessie actief. Stop deze eerst.",
                        webappconfig=WebAppConfig
                        )
        return redirect(url_for('flaskRoutes.charge_sessions'))
    else:
        return render_template("authorize.html", 
                form=form, 
                requesttitle=str("Start laadsessie " + str(id)),
                buttontitle="Start laadsessie",
                errormsg="Het wachtwoord is onjuist",
                webappconfig=WebAppConfig
                )


@flaskRoutes.route("/stop_charge_session/<int:charge_session_id>", methods=["GET", "POST"])
@authenticated_resource
def stop_charge_session(charge_session_id=None):
    global flaskRoutesLogger, WebAppConfig, threadLock
    if charge_session_id is None:
        return jsonify({
            'status': 404, 
            'id': WebAppConfig.ENERGY_DEVICE_ID, 
            'reason': 'Laadsessie niet gevonden'
            })
    # For GET requests, display the authorize form. 
    flaskRoutesLogger.debug('/stop_charge_session {}'.format(request.method))
    if (request.method == 'GET'):
        return render_template("authorize.html", 
            form=AuthorizeForm(),
            requesttitle=str("Stop laadsessie " + str(charge_session_id)),
            buttontitle="Stop laadsessie",
            webappconfig=WebAppConfig
            )
    # For POST requests, login the current user by processing the form.
    form = AuthorizeForm()
    if form.validate_on_submit() and \
       check_password_hash(current_user.password, form.password.data):
        flaskRoutesLogger.debug('stop_charge_session requested and authorized.')
        with threadLock:
            charge_session = ChargeSessionModel.get_one_charge_session(charge_session_id)
            if charge_session is not None:
                WebAppConfig.chThread.end_charge_session(charge_session)
                WebAppConfig.chThread.buzz_ok()
                WebAppConfig.chThread.update_charger_and_led(False)
            else:
                flaskRoutesLogger.warn('Could not stop charge session {}, session not found!'.format(charge_session_id))
        return redirect(url_for('flaskRoutes.charge_sessions'))
    else:
        return render_template("authorize.html", 
                form=form, 
                requesttitle=str("Stop laadsessie " + str(charge_session_id)),
                buttontitle="Stop laadsessie",
                errormsg="Het wachtwoord is onjuist",
                webappconfig=WebAppConfig
                )


@flaskRoutes.route("/usage")
@flaskRoutes.route("/usage/")
@flaskRoutes.route("/usage/<int:cnt>")
def usage(cnt="undefined"):
    global flaskRoutesLogger, WebAppConfig
    flaskRoutesLogger.debug('/usage ' + request.method)
    return render_template("usage_table.html", 
                cnt=cnt,
                webappconfig=WebAppConfig
                )


@flaskRoutes.route("/usage_table")
@flaskRoutes.route("/usage_table/")
@flaskRoutes.route("/usage_table/<int:cnt>")
def usage_table(cnt="undefined"):
    global flaskRoutesLogger, WebAppConfig
    flaskRoutesLogger.debug('/usage_table {} {}'.format(cnt, request.method))
    return render_template("usage_table.html", 
                cnt=cnt,
                webappconfig=WebAppConfig
                )


@flaskRoutes.route("/usage_graph")
@flaskRoutes.route("/usage_graph/")
@flaskRoutes.route("/usage_graph/<int:cnt>")
@authenticated_resource
def usage_graph(cnt="undefined"):
    global flaskRoutesLogger, WebAppConfig
    req_period = request.args['period'] if 'period' in request.args else None
    flaskRoutesLogger.debug('/usage_graph cnt:{} method:{} type:{}'.format(cnt, request.method, req_period))
    return render_template("usage_graph.html", 
                cnt=cnt,
                req_period=req_period,
                webappconfig=WebAppConfig
                )


@flaskRoutes.route("/settings")
@flaskRoutes.route("/settings/")
@flaskRoutes.route("/settings/<int:active>")
@authenticated_resource
def settings(active=1):
    global flaskRoutesLogger, WebAppConfig
    flaskRoutesLogger.debug('/settings {} {}'.format(active, request.method))
    r = Raspberry()
    diag = r.get_all()
    diag['threading'] = {}
    diag['threading']['active_count'] = threading.active_count()
    diag_json = json.dumps(diag)
    # threading.enumerate() not json serializable
    diag['threading']['enum'] = threading.enumerate()
    charger_config_str = ChargerConfigModel().get_config().to_str()
    return render_template("settings.html", 
                active=active, 
                diag=diag, 
                diag_json=diag_json,
                charger_config=charger_config_str,
                energydevicemodel=EnergyDeviceModel.get(),
                webappconfig=WebAppConfig
            )


@flaskRoutes.route("/usage_data")
@flaskRoutes.route("/usage_data/")
@flaskRoutes.route("/usage_data/<int:cnt>")
def usage_data(cnt=100):
    global flaskRoutesLogger
    flaskRoutesLogger.debug('/usage_data {} {}'.format(cnt, request.method))
    device_measurement = EnergyDeviceMeasureModel()
    device_measurement.energy_device_id = WebAppConfig.ENERGY_DEVICE_ID
    qr = device_measurement.get_last_n_saved(energy_device_id=WebAppConfig.ENERGY_DEVICE_ID,n=cnt)
    qr_l = []
    for o in qr:
        qr_l.append(o.to_dict())  

    return jsonify(qr_l)

# Cnt is a maximum to limit impact of this request
@flaskRoutes.route("/usage_data_since/<path:since_timestamp>")
@flaskRoutes.route("/usage_data_since/<path:since_timestamp>/<int:cnt>")
def usage_data_since(since_timestamp, cnt=-1):
    global flaskRoutesLogger
    flaskRoutesLogger.debug('/usage_data_since {} {} {}'.format(since_timestamp, cnt, request.method))
    device_measurement = EnergyDeviceMeasureModel()
    device_measurement.energy_device_id = WebAppConfig.ENERGY_DEVICE_ID
    qr = device_measurement.get_last_n_saved_since(energy_device_id=WebAppConfig.ENERGY_DEVICE_ID,since_ts=since_timestamp,n=cnt)
    qr_l = []
    for o in qr:
        qr_l.append(o.to_dict())  

    return jsonify(qr_l)


@flaskRoutes.route("/active_charge_session", methods=["GET"])
@flaskRoutes.route("/active_charge_session/", methods=["GET"])
# @authenticated_resource
def active_charge_session():
    global WebAppConfig

    flaskRoutesLogger.debug(f'active_charge_session()')
    # Open charge session for this energy device?
    open_charge_session_for_device = \
        ChargeSessionModel.get_open_charge_session_for_device(
                WebAppConfig.ENERGY_DEVICE_ID
        )
    evse = Evse()
    if open_charge_session_for_device is None:
        # None, no active session
        return jsonify({
            'status'            : 404, 
            'id'                : WebAppConfig.ENERGY_DEVICE_ID, 
            'chargeSession'     : False,
            'evseEnabled'       : True if evse.is_enabled() else False,
            'charging'          : True if WebAppConfig.chThread.is_status_charging else False,
            'offPeakEnabled'    : WebAppConfig.peakHoursOffPeakEnabled,
            'offPeakAllowedOnce': WebAppConfig.peakHoursAllowPeakOnePeriod,
            'offPeak'           : True if evse.isOffPeak else False,
            'auth'              : True if (current_user.is_authenticated) else False,
            'reason'            : 'No active charge session'
            })
    try:
        return jsonify({ 
            'status'            : 200,
            'id'                : WebAppConfig.ENERGY_DEVICE_ID, 
            'chargeSession'     : True if open_charge_session_for_device is not None else False,
            'evseEnabled'       : True if evse.is_enabled() else False,
            'charging'          : True if WebAppConfig.chThread.is_status_charging else False,
            'offPeakEnabled'    : WebAppConfig.peakHoursOffPeakEnabled,
            'offPeakAllowedOnce': WebAppConfig.peakHoursAllowPeakOnePeriod,
            'offPeak'           : True if evse.isOffPeak else False,
            'auth'              : True if (current_user.is_authenticated) else False,
            'data'              : open_charge_session_for_device.to_str() if (current_user.is_authenticated) else None
            })
    except Exception as e:
        flaskRoutesLogger.error("active_charge_session - could not return information", exc_info=True)
        pass
    return jsonify({ 
        'status'        : 500, 
        'id'            : WebAppConfig.ENERGY_DEVICE_ID, 
        'reason'        : 'Could not determine charge session'
        })


# Cnt is a maximum to limit impact of this request
@flaskRoutes.route("/charge_sessions")
@flaskRoutes.route("/charge_sessions/")
@authenticated_resource
def charge_sessions(since_timestamp=None):
    global flaskRoutesLogger, WebAppConfig
    flaskRoutesLogger.debug('/charge_sessions {} {}'.format(since_timestamp, request.method))
    jsonRequested = ('CONTENT_TYPE' in request.environ and 
                     request.environ['CONTENT_TYPE'].lower() == 'application/json')
    if (not jsonRequested):
        return render_template("charge_sessions.html",
                    webappconfig=WebAppConfig
                    )
    # Request parameters
    # TODO - format request params and hand to model
    req_from  = request.args['from'] if 'from' in request.args else None
    req_to    = request.args['to'] if 'to' in request.args else None
    req_limit = request.args['limit'] if 'limit' in request.args else None

    charge_sessions = ChargeSessionModel()
    charge_sessions.energy_device_id = WebAppConfig.ENERGY_DEVICE_ID
    qr = charge_sessions.get_last_n_sessions_since(
        energy_device_id=WebAppConfig.ENERGY_DEVICE_ID,
        since_ts=None,
        n=-1
        )
    qr_l = []
    for o in qr:
        qr_l.append(o.to_dict())
    return jsonify(qr_l)


# Cnt is a maximum to limit impact of this request
@flaskRoutes.route("/rfid_tokens", methods=["GET"])
@flaskRoutes.route("/rfid_tokens/", methods=["GET"])
@flaskRoutes.route("/rfid_tokens/<path:token>", methods=["GET", "POST"])
@flaskRoutes.route("/rfid_tokens/<path:token>/", methods=["GET", "POST"])
@authenticated_resource
def rfid_tokens(token=None):
    global flaskRoutesLogger, WebAppConfig
    flaskRoutesLogger.debug('/rfid_tokens {} {}'.format(token, request.method))
    jsonRequested = ('CONTENT_TYPE' in request.environ and 
                     request.environ['CONTENT_TYPE'].lower() == 'application/json')
    flaskRoutesLogger.debug('/rfid_tokens method: {} token: {} jsonRequested: {}'.format(request.method, token, jsonRequested))
    if (not jsonRequested):
        if (token == None):
            return render_template(
                'tokens.html',
                webappconfig=WebAppConfig
                )
        rfid_model = RfidModel().get_one(token)
        if (rfid_model == None):
            return render_template(
                'tokens.html', 
                webappconfig=WebAppConfig
            )
        rfid_model.cleanupOldOAuthToken()    # Remove any expired OAuth token info
        rfid_change_form = RfidChangeForm()
        flaskRoutesLogger.debug('CSRF Token: {}'.format(rfid_change_form.csrf_token.current_token) )
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
                return redirect(url_for('flaskRoutes.rfid_tokens', req_format='html', token=None))
            # TODO - what went wrong? message!
            return render_template("token.html",
                    rfid_model=rfid_model,
                    form=rfid_change_form,
                    webappconfig=WebAppConfig
                )        
        return render_template("token.html",
                    rfid_model=rfid_model,
                    form=rfid_change_form,
                    webappconfig=WebAppConfig
                )        
    # Check if token exist, if not rfid is None
    if (token == None):
        rfid_list = []
        rfid_models = RfidModel().get_all()
        for rfid_model in rfid_models:
            rfid_model.cleanupOldOAuthToken()    # Remove any expired OAuth token info
            rfid_list.append(rfid_model.to_str())
        return jsonify(rfid_list)
    # Specific token
    rfid_model = RfidModel().get_one(token)
    if (rfid_model == None):
        return jsonify({})
    rfid_model.cleanupOldOAuthToken()    # Remove any expired OAuth token info
    return jsonify(rfid_model.to_str())


# Always returns json
@flaskRoutes.route("/rfid_tokens/<path:token>/TeslaAPI/GenerateOAuth", methods=["POST"])
@authenticated_resource  # CSRF Token is valid
def TeslaApi_GenerateOAuth(token=None):
    global flaskRoutesLogger
    flaskRoutesLogger.debug('/rfid_tokens/{}/TeslaAPI/GenerateOAuth {}'.format(token, request.method))
    flaskRoutesLogger.debug('/rfid_tokens/{}/TeslaAPI/GenerateOAuth method: {} token: {}'.format(token, request.method, token))
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

# Always returns json
@flaskRoutes.route("/rfid_tokens/<path:token>/TeslaAPI/RefreshOAuth", methods=["POST"])
@authenticated_resource
def TeslaApi_RefreshOAuth(token=None):
    global flaskRoutesLogger
    flaskRoutesLogger.debug('/rfid_tokens/{}/TeslaAPI/RefreshOAuth {}'.format(token, request.method))
    flaskRoutesLogger.debug('/rfid_tokens/{}/TeslaAPI/RefreshOAuth method: {} token: {}'.format(token, request.method, token))
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

# Always returns json
@flaskRoutes.route("/rfid_tokens/<path:token>/TeslaAPI/RevokeOAuth", methods=["POST"])
@authenticated_resource
def TeslaApi_RevokeOAuth(token=None):
    global flaskRoutesLogger
    flaskRoutesLogger.debug('/rfid_tokens/{}/TeslaAPI/RevokeOAuth {}'.format(token, request.method))
    flaskRoutesLogger.debug('/rfid_tokens/{}/TeslaAPI/RevokeOAuth method: {} token: {}'.format(token, request.method, token))
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


# Always returns json
@flaskRoutes.route("/update_settings/<path:param>/<path:value>", methods=["POST"])
@authenticated_resource  # CSRF Token is valid
def update_settings(param=None, value=None):
    if (param == 'peakHoursOffPeakEnabled'):
        WebAppConfig.peakHoursOffPeakEnabled = True if value.lower() in ['true', '1', 't', 'y', 'yes'] else False
        ophm = OffPeakHoursModel()
        WebSocketUtil.emit(
                event='off_peak_status_update', 
                    id=WebAppConfig.ENERGY_DEVICE_ID,
                    data={ 'isOffPeak': ophm.is_off_peak_now(),
                           'offPeakEnabled': WebAppConfig.peakHoursOffPeakEnabled,
                           'peakAllowOnePeriod': WebAppConfig.peakHoursAllowPeakOnePeriod
                    },
                    namespace='/charge_session',
                    public=True
                )
        return jsonify({ 'status': 200, 'param': param, 'value': WebAppConfig.peakHoursOffPeakEnabled })

    if (param == 'peakHoursAllowPeakOnePeriod'):
        WebAppConfig.peakHoursAllowPeakOnePeriod = True if value.lower() in ['true', '1', 't', 'y', 'yes'] else False
        ophm = OffPeakHoursModel()
        WebSocketUtil.emit(
                event='off_peak_status_update', 
                    id=WebAppConfig.ENERGY_DEVICE_ID,
                    data={ 'isOffPeak': ophm.is_off_peak_now(),
                           'offPeakEnabled': WebAppConfig.peakHoursOffPeakEnabled,
                           'peakAllowOnePeriod': WebAppConfig.peakHoursAllowPeakOnePeriod
                    },
                    namespace='/charge_session',
                    public=True
                )
        return jsonify({ 'status': 200, 'param': param, 'value': WebAppConfig.peakHoursAllowPeakOnePeriod })

    return jsonify({ 'status': 404, 'param': param, 'reason': 'Not found' })
