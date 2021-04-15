import os
import threading
from datetime import datetime, time
from flask import Flask, Blueprint, render_template, abort, request, url_for, redirect, jsonify, session

from flask import current_app as app # Note: that the current_app proxy is only available in the context of a request.

from jinja2.exceptions import TemplateNotFound
from werkzeug.security import generate_password_hash, check_password_hash

from functools import wraps
import json
from json import JSONDecodeError

import logging
import re
from urllib.parse import urlparse, unquote

from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask_socketio import SocketIO, emit

from nl.oppleo.config.OppleoConfig import OppleoConfig
from nl.oppleo.config.OppleoSystemConfig import OppleoSystemConfig

from nl.oppleo.exceptions.Exceptions import (NotAuthorizedException, 
                                             ExpiredException)

from nl.oppleo.models.User import User
from nl.oppleo.webapp.LoginForm import LoginForm
from nl.oppleo.webapp.AuthorizeForm import AuthorizeForm
from nl.oppleo.models.EnergyDeviceMeasureModel import EnergyDeviceMeasureModel
from nl.oppleo.models.Raspberry import Raspberry
from nl.oppleo.models.ChargeSessionModel import ChargeSessionModel
from nl.oppleo.models.RfidModel import RfidModel
from nl.oppleo.models.ChargerConfigModel import ChargerConfigModel
from nl.oppleo.models.ChargeSessionModel import ChargeSessionModel
from nl.oppleo.models.EnergyDeviceModel import EnergyDeviceModel
from nl.oppleo.models.OffPeakHoursModel import OffPeakHoursModel
from nl.oppleo.webapp.ChangePasswordForm import ChangePasswordForm
from nl.oppleo.webapp.RfidChangeForm import RfidChangeForm
from nl.oppleo.api.TeslaApi import TeslaAPI
from nl.oppleo.utils.UpdateOdometerTeslaUtil import UpdateOdometerTeslaUtil
from nl.oppleo.utils.TeslaApiFormatters import formatChargeState, formatVehicle
from nl.oppleo.services.Evse import Evse
from nl.oppleo.utils.WebSocketUtil import WebSocketUtil
from nl.oppleo.utils.GitUtil import GitUtil

from nl.oppleo.utils.EnergyModbusReader import modbusConfigOptions
from nl.oppleo.utils.BackupUtil import BackupUtil

from nl.oppleo.utils.TokenMediator import tokenMediator

# https://en.wikipedia.org/wiki/List_of_HTTP_status_codes
HTTP_CODE_200_OK                    = 200
HTTP_CODE_400_BAD_REQUEST           = 400
HTTP_CODE_401_UNAUTHORIZED          = 401
HTTP_CODE_403_FORBIDDEN             = 403
HTTP_CODE_404_NOT_FOUND             = 404
HTTP_CODE_405_METHOD_NOT_ALLOWED    = 405
HTTP_CODE_409_CONFLICT              = 409
HTTP_CODE_500_INTERNAL_SERVER_ERROR = 500
HTTP_CODE_501_NOT_IMPLEMENTED       = 501

oppleoSystemConfig = OppleoSystemConfig()
oppleoConfig = OppleoConfig()

""" 
 - make sure all url_for routes point to this blueprint
"""
flaskRoutes = Blueprint('flaskRoutes', __name__, template_folder='templates')

flaskRoutesLogger = logging.getLogger('nl.oppleo.webapp.flaskRoutes')
flaskRoutesLogger.debug('Initializing routes')

threadLock = threading.Lock()



def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

def RepresentsFloat(s):
    try: 
        float(s)
        return True
    except ValueError:
        return False



# Resource is only served for logged in user
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
        return ('Niet ingelogd', HTTP_CODE_401_UNAUTHORIZED)
    return decorated

# Resource is only served for logged in user if allowed in preferences
def config_dashboard_access_restriction(function):
    @wraps(function)
    def decorated(*args, **kwargs):
        # Allow dashboard and Usage table access if unrestructed in config
        # request.remote_addr - returns remote address, or IP of reverse proxy
        # request.headers.get('X-Forwarded-For') - returns router address (router is behind the reverse proxy)

        flaskRoutesLogger.debug('config_dashboard_access_restriction() restrictDashboardAccess:{} allowLocalDashboardAccess{} request.remote_addr={} oppleoConfig.routerIPAddress={} current_user.is_authenticated={}'.format(
            oppleoConfig.restrictDashboardAccess, 
            oppleoConfig.allowLocalDashboardAccess,
            request.remote_addr,
            oppleoConfig.routerIPAddress,
            current_user.is_authenticated
            ))

        if (not oppleoConfig.restrictDashboardAccess or \
            ( oppleoConfig.allowLocalDashboardAccess and request.remote_addr != oppleoConfig.routerIPAddress ) or \
            current_user.is_authenticated):
            flaskRoutesLogger.debug('config_dashboard_access_restriction() access allowed')
            return function(*args, **kwargs)
        flaskRoutesLogger.debug('config_dashboard_access_restriction() access denied')
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
        return ('Niet ingelogd', HTTP_CODE_401_UNAUTHORIZED)
    return decorated


@flaskRoutes.route('/', methods=['GET'])
@config_dashboard_access_restriction
def index():
    global flaskRoutesLogger, oppleoConfig
    flaskRoutesLogger.debug('/ {}'.format(request.method))
    try:
        return render_template(
            'dashboard.html',
            oppleoconfig=oppleoConfig
            )
    except TemplateNotFound:
        abort(HTTP_CODE_404_NOT_FOUND)
    except Exception as e:
        flaskRoutesLogger.debug('/  - exception')
        flaskRoutesLogger.debug(e)

@flaskRoutes.route("/home")
#@authenticated_resource
@config_dashboard_access_restriction
def home():
    global flaskRoutesLogger
    flaskRoutesLogger.debug('/home {}'.format(request.method))
    return redirect('/')

# 400 Bad Request
@flaskRoutes.errorhandler(HTTP_CODE_400_BAD_REQUEST)
def page_not_found(e):
    global flaskRoutesLogger
    flaskRoutesLogger.debug('400 bad request error handler')
    # No need for oppleoconfig=oppleoConfig
    return render_template('errorpages/400.html'), HTTP_CODE_400_BAD_REQUEST

# 404 Not Found
@flaskRoutes.errorhandler(HTTP_CODE_404_NOT_FOUND)
def bad_request(e):
    global flaskRoutesLogger
    flaskRoutesLogger.debug('404 page not found error handler')
    # No need for oppleoconfig=oppleoConfig
    return render_template('errorpages/404.html'), HTTP_CODE_404_NOT_FOUND

# 500 Internal Server
@flaskRoutes.errorhandler(HTTP_CODE_500_INTERNAL_SERVER_ERROR)
def internal_server_error(e):
    global flaskRoutesLogger
    flaskRoutesLogger.debug('500 internal_server_error error handler')
    # No need for oppleoconfig=oppleoConfig
    return render_template('errorpages/500.html'), HTTP_CODE_500_INTERNAL_SERVER_ERROR


@flaskRoutes.route('/login', methods=['GET', 'POST'])
def login():
    # For GET requests, display the login form. 
    global flaskRoutesLogger, oppleoConfig
    flaskRoutesLogger.debug('/login {}'.format(request.method))
    if (request.method == 'GET'):
        return render_template("login.html", 
            form=LoginForm(),
            oppleoconfig=oppleoConfig
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
                oppleoconfig=oppleoConfig
                )



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
    global flaskRoutesLogger, oppleoConfig
    flaskRoutesLogger.debug('/change_password {}'.format(request.method))
    if (request.method == 'GET'):
        return render_template(
            'change_password.html', 
            form=ChangePasswordForm(),
            oppleoconfig=oppleoConfig
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
            oppleoconfig=oppleoConfig
            )
    if form.validate_on_submit():
        # Valid, change the password for the user now
        user = current_user
        user.password = generate_password_hash(form.new_password.data)
        user.save()
        return render_template(
            'change_password_success.html', 
            oppleoconfig=oppleoConfig
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
        oppleoconfig=oppleoConfig
        )


@flaskRoutes.route("/about")
@flaskRoutes.route("/about/")
def about():
    global flaskRoutesLogger, oppleoConfig
    flaskRoutesLogger.debug('/about {}'.format(request.method))
    return render_template("about.html",
                oppleoconfig=oppleoConfig
                )


@flaskRoutes.route("/shutdown", methods=["GET", "POST"])
@flaskRoutes.route("/shutdown/", methods=["GET", "POST"])
@authenticated_resource
def shutdown():
    global flaskRoutesLogger, oppleoConfig
    # For GET requests, display the authorize form. 
    flaskRoutesLogger.debug('/shutdown {}'.format(request.method))
    if (request.method == 'GET'):
        return render_template("authorize.html", 
            form=AuthorizeForm(),
            requesttitle="Uitschakelen",
            requestdescription="Schakel het systeem helemaal uit.<br/>Doe dit alleen voor onderhoud aan het systeem. Voor opnieuw opstarten is fysieke toegang tot het systeem vereist!",
            buttontitle="Schakel uit!",
            oppleoconfig=oppleoConfig
            )
    # For POST requests, login the current user by processing the form.
    form = AuthorizeForm()
    if form.validate_on_submit() and \
       check_password_hash(current_user.password, form.password.data):
        flaskRoutesLogger.debug('Shutdown requested and authorized.')
        if BackupUtil().backupInProgress:
            # Cannot shutdown now, wait for backup to complete
            flaskRoutesLogger.debug('Restart request denied. Backup in progress.')
            return render_template("authorize.html", 
                    form=form, 
                    requesttitle="Uitschakelen",
                    requestdescription="Schakel het systeem helemaal uit.<br/>Doe dit alleen voor onderhoud aan het systeem. Voor opnieuw opstarten is fysieke toegang tot het systeem vereist!",
                    buttontitle="Schakel uit!",
                    errormsg="Er wordt momenteel een backup gemaakt. Probeer het later normaals.",
                    oppleoconfig=oppleoConfig
                    )
        flaskRoutesLogger.debug('Shutting down in 2 seconds...')
        # Simple os.system('sudo shutdown now') initiates shutdown before a webpage can be returned
        os.system("nohup sudo -b bash -c 'sleep 2; shutdown now' &>/dev/null")
        return render_template("shuttingdown.html", 
                    oppleoconfig=oppleoConfig
                    )
    else:
        return render_template("authorize.html", 
                form=form, 
                requesttitle="Uitschakelen",
                requestdescription="Schakel het systeem helemaal uit.<br/>Doe dit alleen voor onderhoud aan het systeem. Voor opnieuw opstarten is fysieke toegang tot het systeem vereist!",
                buttontitle="Schakel uit!",
                errormsg="Het wachtwoord is onjuist",
                oppleoconfig=oppleoConfig
                )


@flaskRoutes.route("/reboot", methods=["GET", "POST"])
@flaskRoutes.route("/reboot/", methods=["GET", "POST"])
@authenticated_resource
def reboot():
    global flaskRoutesLogger, oppleoConfig
    # For GET requests, display the authorize form. 
    flaskRoutesLogger.debug('/reboot {}'.format(request.method))
    if (request.method == 'GET'):
        return render_template("authorize.html", 
            form=AuthorizeForm(),
            requesttitle="Reboot",
            requestdescription="Reboot het systeem.<br/>Doe dit alleen als het systeem zich inconsistent gedraagd. <br />Dit zal ongeveer 40 seconden duren.",
            buttontitle="Reboot!",
            oppleoconfig=oppleoConfig
            )
    # For POST requests, login the current user by processing the form.
    form = AuthorizeForm()
    if form.validate_on_submit() and \
       check_password_hash(current_user.password, form.password.data):
        flaskRoutesLogger.debug('Reboot requested and authorized.')
        if BackupUtil().backupInProgress:
            # Cannot reboot now, wait for backup to complete
            flaskRoutesLogger.debug('Reboot request denied. Backup in progress.')
            return render_template("authorize.html", 
                    form=form, 
                    requesttitle="Reboot",
                    requestdescription="Reboot het systeem.<br/>Doe dit alleen als het systeem zich inconsistent gedraagd. <br />Dit zal ongeveer 40 seconden duren.",
                    buttontitle="Reboot!",
                    errormsg="Er wordt momenteel een backup gemaakt. Probeer het later normaals.",
                    oppleoconfig=oppleoConfig
                    )
        flaskRoutesLogger.debug('Rebooting in 2 seconds...')
        # Simple os.system('sudo reboot') initiates reboot before a webpage can be returned
        os.system("nohup sudo -b bash -c 'sleep 2; reboot' &>/dev/null")
        return render_template("rebooting.html", 
                    oppleoconfig=oppleoConfig
                    )
    else:
        return render_template("authorize.html", 
                form=form, 
                requesttitle="Reboot",
                requestdescription="Reboot het systeem.<br/>Doe dit alleen als het systeem zich inconsistent gedraagd. <br />Dit zal ongeveer 40 seconden duren.",
                buttontitle="Reboot!",
                errormsg="Het wachtwoord is onjuist",
                oppleoconfig=oppleoConfig
                )


@flaskRoutes.route("/restart", methods=["GET", "POST"])
@flaskRoutes.route("/restart/", methods=["GET", "POST"])
@authenticated_resource
def restart():
    global flaskRoutesLogger, oppleoConfig
    # For GET requests, display the authorize form. 
    flaskRoutesLogger.debug('/restart {}'.format(request.method))
    if (request.method == 'GET'):
        return render_template("authorize.html", 
            form=AuthorizeForm(),
            requesttitle="Herstarten",
            requestdescription="Herstart de applicatie.<br/>Doe dit alleen als een nieuwe configuratie geladen moet worden. Het herstarten van de applicatie duurt ongeveer 10 seconden.",
            buttontitle="Herstart!",
            oppleoconfig=oppleoConfig
            )
    # For POST requests, login the current user by processing the form.
    form = AuthorizeForm()
    if form.validate_on_submit() and \
       check_password_hash(current_user.password, form.password.data):
        if BackupUtil().backupInProgress:
            # Cannot restart now, wait for backup to complete
            flaskRoutesLogger.debug('Restart request denied. Backup in progress.')
            return render_template("authorize.html", 
                    form=form, 
                    requesttitle="Herstarten",
                    requestdescription="Herstart de applicatie.<br/>Doe dit alleen als een nieuwe configuratie geladen moet worden. Het herstarten van de applicatie duurt ongeveer 10 seconden.",
                    buttontitle="Herstart!",
                    errormsg="Er wordt momenteel een backup gemaakt. Probeer het later normaals.",
                    oppleoconfig=oppleoConfig
                    )

        flaskRoutesLogger.debug('Restart requested and authorized. Restarting in 2 seconds...')
        # Simple os.system('sudo systemctl restart Oppleo.service') initiates restart before a webpage can be returned
        try:
            os.system("nohup sudo -b bash -c 'sleep 2; systemctl restart Oppleo.service' &>/dev/null")
        except Exception as e:
            pass
        return render_template("restarting.html", 
                    oppleoconfig=oppleoConfig
                    )
    else:
        return render_template("authorize.html", 
                form=form, 
                requesttitle="Herstarten",
                requestdescription="Herstart de applicatie.<br/>Doe dit alleen als een nieuwe configuratie geladen moet worden. Het herstarten van de applicatie duurt ongeveer 10 seconden.",
                buttontitle="Herstart!",
                errormsg="Het wachtwoord is onjuist",
                oppleoconfig=oppleoConfig
                )


@flaskRoutes.route("/software-update", methods=["GET", "POST"])
@flaskRoutes.route("/software-update/", methods=["GET", "POST"])
@authenticated_resource
def software_update():
    global flaskRoutesLogger, oppleoConfig
    # For GET requests, display the authorize form. 
    flaskRoutesLogger.debug('/software-update {}'.format(request.method))
    if (oppleoConfig.softwareUpdateInProgress):
        # 409 Conflict - Request conflicts with the current state of the server
        abort(409)
    if (request.method == 'GET'):
        return render_template("authorize.html", 
            form=AuthorizeForm(),
            requesttitle="Software Update",
            requestdescription="Update de applicatie.<br/>Doe dit alleen als een nieuwe configuratie geladen moet worden. Het updaten van de applicatie kan 30 seconden tot 1 minuut duren.",
            requestdescriptionclass="text-center text-warning",
            buttontitle="Update!",
            oppleoconfig=oppleoConfig
            )
    # For POST requests, login the current user by processing the form.
    form = AuthorizeForm()
    if form.validate_on_submit() and \
       check_password_hash(current_user.password, form.password.data):
        flaskRoutesLogger.debug('Software update requested and authorized.')
        if BackupUtil().backupInProgress:
            # Cannot start software update now, wait for backup to complete
            flaskRoutesLogger.debug('Software update request denied. Backup in progress.')
            return render_template("authorize.html", 
                    form=form, 
                    requesttitle="Software Update",
                    requestdescription="Update de applicatie.<br/>Doe dit alleen als een nieuwe configuratie geladen moet worden. Het updaten van de applicatie kan 30 seconden tot 1 minuut duren.",
                    buttontitle="Herstart!",
                    errormsg="Er wordt momenteel een backup gemaakt. Probeer het later normaals.",
                    oppleoconfig=oppleoConfig
                    )

        flaskRoutesLogger.debug('Updating in 2 seconds...')
        try: 
            updateSoftwareInstallCmd = os.path.join(os.path.dirname(os.path.realpath(__file__)).split('src/nl/oppleo/webapp')[0], 'install/install.sh')
            updateSoftwareLogFile = os.path.join(os.path.dirname(os.path.realpath(__file__)).split('src/nl/oppleo/webapp')[0], 'install/log/update_{}.log'.format(datetime.now().strftime("%Y%m%d%H%M%S")))
            # os.system("nohup sudo -b bash -c 'sleep 2; /home/pi/Oppleo/install/install.sh service' &>/dev/null")
            flaskRoutesLogger.debug("nohup sudo -u pi -b bash -c 'sleep 2; {} service &> {}'".format(updateSoftwareInstallCmd, updateSoftwareLogFile))
            os.popen("nohup sudo -u pi -b bash -c 'sleep 2; {} &> {}'".format(updateSoftwareInstallCmd, updateSoftwareLogFile))
            # update script kills Oppleo, and also os.system or os.popen processes. Spawn new process that will survive the Oppleo kill
            oppleoConfig.softwareUpdateInProgress = True
        except Exception as e:
            flaskRoutesLogger.error("Exception running software update! {}".format(e))
        return render_template("softwareupdate.html", 
                    oppleoconfig=oppleoConfig
                    )
    else:
        return render_template("authorize.html", 
                form=form, 
                requesttitle="Software Update",
                requestdescription="Update de applicatie.<br/>Doe dit alleen als een nieuwe configuratie geladen moet worden. Het updaten van de applicatie kan 30 seconden tot 1 minuut duren.",
                buttontitle="Herstart!",
                errormsg="Het wachtwoord is onjuist",
                oppleoconfig=oppleoConfig
                )


@flaskRoutes.route("/delete_charge_session/<int:id>", methods=["GET", "POST"])
@flaskRoutes.route("/delete_charge_session/<int:id>/", methods=["GET", "POST"])
@authenticated_resource
def delete_charge_session(id=None):
    global flaskRoutesLogger, oppleoConfig
    if id is None:
        return jsonify({
            'status': HTTP_CODE_404_NOT_FOUND, 
            'id': oppleoConfig.chargerName, 
            'reason': 'Laadsessie niet gevonden'
            })
    # For GET requests, display the authorize form. 
    flaskRoutesLogger.debug('/delete_charge_session {}'.format(request.method))
    if (request.method == 'GET'):
        return render_template("authorize.html", 
            form=AuthorizeForm(),
            requesttitle=str("Laadsessie " + str(id)),
            buttontitle=str("Verwijder laadsessie " + str(id)),
            oppleoconfig=oppleoConfig
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
                oppleoconfig=oppleoConfig
                )


@flaskRoutes.route("/start_charge_session/<path:token>", methods=["GET", "POST"])
@flaskRoutes.route("/start_charge_session/<path:token>/", methods=["GET", "POST"])
@authenticated_resource
def start_charge_session(token=None):
    global flaskRoutesLogger, oppleoConfig, threadLock

    # Page to forward to after succesful authorization
    # None | dashboard | charge_sessions
    next_page = request.args.get('next_page')

    if token is None:
        return jsonify({
            'status': HTTP_CODE_404_NOT_FOUND, 
            'id': oppleoConfig.chargerName, 
            'reason': 'RFID token niet gevonden'
            })

    # For GET requests, display the authorize form. 
    flaskRoutesLogger.debug('/start_charge_session {}'.format(request.method))
    # Authorization required?
    if (oppleoConfig.authWebCharge and request.method == 'GET'):
        return render_template("authorize.html", 
            form=AuthorizeForm(next_page=next_page),
            requesttitle=str("Start laadsessie"),
            buttontitle="Start laadsessie",
            oppleoconfig=oppleoConfig
            )
    # For POST requests, login the current user by processing the form.
    form = AuthorizeForm(next_page=next_page)
    if (not oppleoConfig.authWebCharge) or (                                  \
            form.validate_on_submit() and                                  \
            check_password_hash(current_user.password, form.password.data) \
            ):
        flaskRoutesLogger.debug('start_charge_session requested. authorized with authWebCharge={}.'.format(oppleoConfig.authWebCharge))

        with threadLock:
            charge_session = ChargeSessionModel.get_open_charge_session_for_device(oppleoConfig.chargerName)
            if charge_session is None:
                if oppleoConfig.chThread.rfidAuthorized(token):
                    oppleoConfig.chThread.start_charge_session(
                                    rfid=token,
                                    trigger=ChargeSessionModel.TRIGGER_WEB,
                                    condense=False
                                )
                    oppleoConfig.chThread.buzz_ok()
                    oppleoConfig.chThread.update_charger_and_led(True)
                else:
                    rfidToken = RfidModel.get_one(token)

                    if not rfidToken.enabled:
                        flaskRoutesLogger.warn('Could not start charge session for rfid {} [{}], NotAuthorized!'.format(rfidToken.name, token))
                        return render_template("errorpages/405-NotAuthorizedException.html",
                                requesttitle=str("RFID token niet actief!"),
                                buttontitle="Terug",
                                errormsg="RFID token \"" + str(rfidToken.name) + "\" [" + str(token) + "] is niet geautoriseerd om een laadsessie te starten."
                                )
                   
                    if oppleoConfig.chThread.isExpired(rfidToken.valid_from, rfidToken.valid_until):
                        rfidToken = RfidModel.get_one(token)
                        flaskRoutesLogger.warn('Could not start charge session for rfid {}. Expired!'.format(token))
                        return render_template("errorpages/401-ExpiredException.html", 
                                requesttitle=str("RFID token niet geldig!"),
                                buttontitle="Start laadsessie",
                                errormsg="De geldigheid van RFID token \"" + str(rfidToken.name) + "\" [" + str(token) + "] is verlopen."
                                )
                    # No other option
                    return render_template('errorpages/500.html'), HTTP_CODE_500_INTERNAL_SERVER_ERROR
            else:
                # A charge session was started elsewhere, fail
                flaskRoutesLogger.warn('Could not start charge session for rfid {}, already session active!'.format(token))
                return render_template("authorize.html", 
                        form=form, 
                        requesttitle=str("Start laadsessie " + str(token)),
                        buttontitle="Start laadsessie",
                        errormsg="Er is al een laadsessie actief. Stop deze eerst.",
                        oppleoconfig=oppleoConfig
                        )
        if isinstance(next_page, str) and next_page.lower() == 'charge_sessions':
            return redirect(url_for('flaskRoutes.charge_sessions'))
        if isinstance(next_page, str) and next_page.lower() == 'dashboard':
            return redirect(url_for('flaskRoutes.home'))
        return redirect(url_for('flaskRoutes.charge_sessions'))
    else:
        return render_template("authorize.html", 
                form=form, 
                requesttitle=str("Start laadsessie " + str(token)),
                buttontitle="Start laadsessie",
                errormsg="Het wachtwoord is onjuist",
                oppleoconfig=oppleoConfig
                )


@flaskRoutes.route("/stop_charge_session/<int:charge_session_id>", methods=["GET", "POST"])
@flaskRoutes.route("/stop_charge_session/<int:charge_session_id>/", methods=["GET", "POST"])
@authenticated_resource
def stop_charge_session(charge_session_id=None):
    global flaskRoutesLogger, oppleoConfig, threadLock

    # Page to forward to after succesful authorization
    # None | dashboard | charge_sessions
    next_page = request.args.get('next_page')

    if charge_session_id is None:
        return jsonify({
            'status': HTTP_CODE_404_NOT_FOUND, 
            'id': oppleoConfig.chargerName, 
            'reason': 'Laadsessie niet gevonden'
            })
    # For GET requests, display the authorize form. 
    flaskRoutesLogger.debug('/stop_charge_session {}'.format(request.method))
    # Authorization required?
    if (oppleoConfig.authWebCharge and request.method == 'GET'):
        return render_template("authorize.html", 
            form=AuthorizeForm(next_page=next_page),
            requesttitle=str("Stop laadsessie " + str(charge_session_id)),
            buttontitle="Stop laadsessie",
            oppleoconfig=oppleoConfig
            )
    # For POST requests, login the current user by processing the form.
    form = AuthorizeForm(next_page=next_page)

    if (not oppleoConfig.authWebCharge) or (                                  \
            form.validate_on_submit() and                                  \
            check_password_hash(current_user.password, form.password.data) \
            ):
        flaskRoutesLogger.debug('stop_charge_session requested. authorized with authWebCharge={}.'.format(oppleoConfig.authWebCharge))

        with threadLock:
            charge_session = ChargeSessionModel.get_one_charge_session(charge_session_id)
            if charge_session is not None:
                # End session now, through WEB, not detecting the latest consumption
                oppleoConfig.chThread.end_charge_session(charge_session, False)
                oppleoConfig.chThread.buzz_ok()
                oppleoConfig.chThread.update_charger_and_led(False)
            else:
                flaskRoutesLogger.warn('Could not stop charge session {}, session not found!'.format(charge_session_id))
        if isinstance(next_page, str) and next_page.lower() == 'charge_sessions':
            return redirect(url_for('flaskRoutes.charge_sessions'))
        if isinstance(next_page, str) and next_page.lower() == 'dashboard':
            return redirect(url_for('flaskRoutes.home'))
        return redirect(url_for('flaskRoutes.charge_sessions'))
    else:
        return render_template("authorize.html", 
                form=form, 
                requesttitle=str("Stop laadsessie " + str(charge_session_id)),
                buttontitle="Stop laadsessie",
                errormsg="Het wachtwoord is onjuist",
                oppleoconfig=oppleoConfig
                )


@flaskRoutes.route("/usage")
@flaskRoutes.route("/usage/")
@flaskRoutes.route("/usage/<int:cnt>")
@flaskRoutes.route("/usage/<int:cnt>/")
@config_dashboard_access_restriction
def usage(cnt="undefined"):
    global flaskRoutesLogger, oppleoConfig
    flaskRoutesLogger.debug('/usage ' + request.method)
    return render_template("usage_table.html", 
                cnt=cnt,
                oppleoconfig=oppleoConfig
                )


@flaskRoutes.route("/usage_table")
@flaskRoutes.route("/usage_table/")
@flaskRoutes.route("/usage_table/<int:cnt>")
@flaskRoutes.route("/usage_table/<int:cnt>/")
@config_dashboard_access_restriction
def usage_table(cnt="undefined"):
    global flaskRoutesLogger, oppleoConfig
    try:
        cnt = int(request.args['cnt']) if 'cnt' in request.args else cnt
    except ValueError:
        flaskRoutesLogger.debug('/usage_table could not convert cnt to integer number')

    flaskRoutesLogger.debug('/usage_table {} {}'.format(cnt, request.method))
    return render_template("usage_table.html", 
                cnt=cnt,
                oppleoconfig=oppleoConfig
                )


@flaskRoutes.route("/usage_graph")
@flaskRoutes.route("/usage_graph/")
@flaskRoutes.route("/usage_graph/<int:cnt>")
@flaskRoutes.route("/usage_graph/<int:cnt>/")
@authenticated_resource
def usage_graph(cnt="undefined"):
    global flaskRoutesLogger, oppleoConfig
    req_period = request.args['period'] if 'period' in request.args else None
    flaskRoutesLogger.debug('/usage_graph cnt:{} method:{} type:{}'.format(cnt, request.method, req_period))
    return render_template("usage_graph.html", 
                cnt=cnt,
                req_period=req_period,
                oppleoconfig=oppleoConfig
                )



@flaskRoutes.route("/settings")
@flaskRoutes.route("/settings/")
@flaskRoutes.route("/settings/<int:active>")
@flaskRoutes.route("/settings/<int:active>/")
@authenticated_resource
def settings(active=1):
    global flaskRoutesLogger, oppleoConfig, oppleoSystemConfig, modbusConfigOptions
    flaskRoutesLogger.debug('/settings {} {}'.format(active, request.method))
    r = Raspberry()
    diag = r.get_all()
    diag['threading'] = {}
    diag['threading']['active_count'] = threading.active_count()
    diag_json = json.dumps(diag)
    # threading.enumerate() not json serializable
    diag['threading']['enum'] = threading.enumerate()
    # OffPeakHoursModel not resializable
    diag['offPeak'] = {}
    diag['offPeak']['allReps'] = OffPeakHoursModel.get_all_representations_nl()
    diag['offPeak']['all'] = OffPeakHoursModel.get_all()

    diag['offPeak']['monday'] = OffPeakHoursModel.get_monday()
    diag['offPeak']['tuesday'] = OffPeakHoursModel.get_tuesday()
    diag['offPeak']['wednesday'] = OffPeakHoursModel.get_wednesday()
    diag['offPeak']['thursday'] = OffPeakHoursModel.get_thursday()
    diag['offPeak']['friday'] = OffPeakHoursModel.get_friday()
    diag['offPeak']['saturday'] = OffPeakHoursModel.get_saturday()
    diag['offPeak']['sunday'] = OffPeakHoursModel.get_sunday()

    diag['modbusConfigOptions'] = modbusConfigOptions

    diag['lastSoftwareUpdate'] = GitUtil.lastBranchGitDateStr()

    charger_config_str = ChargerConfigModel().get_config().to_str()
    return render_template("settings.html", 
                active=active, 
                diag=diag, 
                diag_json=diag_json,
                charger_config=charger_config_str,
                energydevicemodel=EnergyDeviceModel.get(),
                oppleosystemconfig=oppleoSystemConfig,
                oppleoconfig=oppleoConfig,
                backuputil=BackupUtil()
            )


@flaskRoutes.route("/usage_data")
@flaskRoutes.route("/usage_data/")
@flaskRoutes.route("/usage_data/<int:cnt>")
@flaskRoutes.route("/usage_data/<int:cnt>/")
@config_dashboard_access_restriction
def usage_data(cnt=100):
    global flaskRoutesLogger
    flaskRoutesLogger.debug('/usage_data {} {}'.format(cnt, request.method))
    device_measurement = EnergyDeviceMeasureModel()
    device_measurement.energy_device_id = oppleoConfig.chargerName
    qr = device_measurement.get_last_n_saved(energy_device_id=oppleoConfig.chargerName,n=cnt)
    qr_l = []
    for o in qr:
        qr_l.append(o.to_dict())  

    return jsonify(qr_l)

# Cnt is a maximum to limit impact of this request
@flaskRoutes.route("/usage_data_since/<path:since_timestamp>")
@flaskRoutes.route("/usage_data_since/<path:since_timestamp>/")
@flaskRoutes.route("/usage_data_since/<path:since_timestamp>/<int:cnt>")
@flaskRoutes.route("/usage_data_since/<path:since_timestamp>/<int:cnt>/")
@config_dashboard_access_restriction
def usage_data_since(since_timestamp, cnt=-1):
    global flaskRoutesLogger
    flaskRoutesLogger.debug('/usage_data_since {} {} {}'.format(since_timestamp, cnt, request.method))
    device_measurement = EnergyDeviceMeasureModel()
    device_measurement.energy_device_id = oppleoConfig.chargerName
    qr = device_measurement.get_last_n_saved_since(energy_device_id=oppleoConfig.chargerName,since_ts=since_timestamp,n=cnt)
    qr_l = []
    for o in qr:
        qr_l.append(o.to_dict())  

    return jsonify(qr_l)


@flaskRoutes.route("/active_charge_session", methods=["GET"])
@flaskRoutes.route("/active_charge_session/", methods=["GET"])
# @authenticated_resource
@config_dashboard_access_restriction
def active_charge_session():
    global oppleoConfig

    flaskRoutesLogger.debug(f'active_charge_session()')
    # Open charge session for this energy device?
    open_charge_session_for_device = \
        ChargeSessionModel.get_open_charge_session_for_device(
                oppleoConfig.chargerName
        )
    evse = Evse()
    if open_charge_session_for_device is None:
        # None, no active session
        return jsonify({
            'status'            : HTTP_CODE_404_NOT_FOUND, 
            'id'                : oppleoConfig.chargerName, 
            'chargeSession'     : False,
            'evseEnabled'       : True if evse.is_enabled() else False,
            'charging'          : True if oppleoConfig.chThread is not None and oppleoConfig.chThread.is_status_charging else False,
            'offPeakEnabled'    : oppleoConfig.offpeakEnabled,
            'offPeakAllowedOnce': oppleoConfig.allowPeakOnePeriod,
            'offPeak'           : True if evse.isOffPeak else False,
            'auth'              : True if (current_user.is_authenticated) else False,
            'reason'            : 'No active charge session'
            })
    try:
        rfid_data = RfidModel.get_one(open_charge_session_for_device.rfid)
        return jsonify({ 
            'status'            : HTTP_CODE_200_OK,
            'id'                : oppleoConfig.chargerName, 
            'chargeSession'     : True if open_charge_session_for_device is not None else False,
            'evseEnabled'       : True if evse.is_enabled() else False,
            'charging'          : True if oppleoConfig.chThread.is_status_charging else False,
            'offPeakEnabled'    : oppleoConfig.offpeakEnabled,
            'offPeakAllowedOnce': oppleoConfig.allowPeakOnePeriod,
            'offPeak'           : True if evse.isOffPeak else False,
            'auth'              : True if (current_user.is_authenticated) else False,
            'data'              : open_charge_session_for_device.to_str() if (current_user.is_authenticated) else None,
            'rfid'              : rfid_data.to_str() if (current_user.is_authenticated) else None
            })
    except Exception as e:
        flaskRoutesLogger.error("active_charge_session - could not return information", exc_info=True)
        pass
    return jsonify({ 
        'status'        : HTTP_CODE_500_INTERNAL_SERVER_ERROR, 
        'id'            : oppleoConfig.chargerName, 
        'reason'        : 'Could not determine charge session'
        })


'''
    Cnt is a maximum to limit impact of this request
    req_from and req_to are date string ('%d/%m/%Y, %H:%M:%S')
    Date values as zero-padded decimal number (01, 02, ...) and month 1-based (Jan = 1)
'''
@flaskRoutes.route("/charge_sessions", methods=["GET"])
@flaskRoutes.route("/charge_sessions/", methods=["GET"])
@authenticated_resource
def charge_sessions(since_timestamp=None):
    global flaskRoutesLogger, oppleoConfig
    flaskRoutesLogger.debug('/charge_sessions {}'.format(request.method))
    jsonRequested = ('CONTENT_TYPE' in request.environ and 
                     request.environ['CONTENT_TYPE'].lower() == 'application/json')
    if (not jsonRequested):
        return render_template("charge_sessions.html",
                    oppleoconfig=oppleoConfig
                    )
    # Request parameters - format and hand to model (format 01-02-2020, 00:00:00)
    req_from  = None
    req_to    = None
    req_limit = -1
    try:
        req_from  = request.args['from'] if 'from' in request.args else None
        req_to    = request.args['to'] if 'to' in request.args else None
        req_limit = int(request.args['limit']) if 'limit' in request.args else -1
    except Exception as e:
        flaskRoutesLogger.warning('/charge_sessions exception formatting arguments {}'.format(str(e)))
        pass
    flaskRoutesLogger.debug('/charge_sessions req_from:{} req_to:{} req_limit:{}'.format(req_from, req_to, req_limit))

    charge_sessions = ChargeSessionModel()
    charge_sessions.energy_device_id = oppleoConfig.chargerName

    qr = []
    try:
        qr = charge_sessions.get_max_n_sessions_between(
            energy_device_id=oppleoConfig.chargerName, 
            from_ts=req_from, 
            to_ts=req_to,
            n=req_limit
            )
    except Exception as e:
        flaskRoutesLogger.warning('/charge_sessions exception ChargeSessionModel.get_max_n_sessions_between {}'.format(str(e)))
        abort(HTTP_CODE_500_INTERNAL_SERVER_ERROR)
        pass

    """
    qr = charge_sessions.get_last_n_sessions_since(
        energy_device_id=oppleoConfig.chargerName,
        since_ts=None,
        n=-1
        )
    """
    qr_l = []
    for o in qr:
        qr_l.append(o.to_dict())
    return jsonify(qr_l)


@flaskRoutes.route("/charge_history", methods=["GET"])
@flaskRoutes.route("/charge_history/", methods=["GET"])
@authenticated_resource
def charge_history():
    global flaskRoutesLogger, oppleoConfig
    flaskRoutesLogger.debug('/charge_history {}'.format(request.method))
    jsonRequested = ('CONTENT_TYPE' in request.environ and 
                     request.environ['CONTENT_TYPE'].lower() == 'application/json')
    if (not jsonRequested):
        return render_template("charge_history.html",
                oppleoconfig=oppleoConfig
                )
    # Return history
    charge_sessions = ChargeSessionModel()
    charge_sessions.energy_device_id = oppleoConfig.chargerName

    csh = []
    try:
        # Return with no year and month is the open session (no end time)
        csh = charge_sessions.get_history()
    except Exception as e:
        flaskRoutesLogger.warning('/charge_history exception ChargeSessionModel.get_history {}'.format(str(e)))
        abort(HTTP_CODE_500_INTERNAL_SERVER_ERROR)
        pass

    csh_l = []
    for o in csh:
        csh_l.append({ 'Year': o.Year,
                      'Month': o.Month,
                      'TotalEnergy': o.TotalEnergy,
                      'TotalEnergyUnit': 'kWh',
                      'TotalPrice': o.TotalPrice,
                      'TotalPriceUnit': '€'
                    })
    return jsonify(csh_l)



@flaskRoutes.route("/charge_report/<int:year>/<int:month>")
@flaskRoutes.route("/charge_report/<int:year>/<int:month>/")
@authenticated_resource
def charge_report(year=-1, month=-1):
    global flaskRoutesLogger, oppleoConfig
    '''
        year    - actual year
        month   - zero based month (0-11)
        the html file uses js to obtain the data
    '''
    flaskRoutesLogger.debug('/charge_report {} {} {}'.format(year, month, request.method))
    return render_template("charge_report.html",
                year=year,
                month=month,
                oppleoconfig=oppleoConfig
                )


@flaskRoutes.route("/rfid_tokens/<path:token>/create", methods=["POST"])
@flaskRoutes.route("/rfid_tokens/<path:token>/create/", methods=["POST"])
@authenticated_resource
def rfid_token_create(token=None):
    flaskRoutesLogger.debug('{} /rfid_tokens/{}/create'.format(request.method, token))

    # does this rfid exits?
    rfid_data = RfidModel.get_one(token)
    if rfid_data is not None:
        # 403 Forbidden
        return json.dumps({'success': False, 'token': token, 'status': 403, 'description': 'Existing token'}), 403, {'ContentType':'application/json'} 

    # does not exist, new id
    new_rfid_entry = RfidModel()
    new_rfid_entry.set({"rfid": token})
    new_rfid_entry.save()
    # 201 created
    return json.dumps({'success': True, 'token': token, 'status': 201}), 201, {'ContentType':'application/json'} 



# Cnt is a maximum to limit impact of this request
@flaskRoutes.route("/rfid_tokens", methods=["GET"])
@flaskRoutes.route("/rfid_tokens/", methods=["GET"])
@flaskRoutes.route("/rfid_tokens/<path:token>", methods=["GET", "POST", "DELETE"])
@flaskRoutes.route("/rfid_tokens/<path:token>/", methods=["GET", "POST", "DELETE"])
@authenticated_resource
def rfid_tokens(token=None):
    global flaskRoutesLogger, oppleoConfig
    flaskRoutesLogger.debug('/rfid_tokens {} {}'.format(token, request.method))
    jsonRequested = ('CONTENT_TYPE' in request.environ and 
                     request.environ['CONTENT_TYPE'].lower() == 'application/json')
    flaskRoutesLogger.debug('/rfid_tokens method: {} token: {} jsonRequested: {}'.format(request.method, token, jsonRequested))
    if (not jsonRequested):
        if (token == None):
            return render_template(
                'tokens.html',
                oppleoconfig=oppleoConfig
                )
        rfid_model = RfidModel().get_one(token)
        if (rfid_model == None):
            return render_template(
                'tokens.html', 
                oppleoconfig=oppleoConfig
            )
        rfid_model.cleanupOldOAuthToken()    # Remove any expired OAuth token info
        rfid_change_form = RfidChangeForm()
        flaskRoutesLogger.debug('CSRF Token: {}'.format(rfid_change_form.csrf_token.current_token) )
        if (request.method == 'DELETE'):
            # Not allowed
            abort(405)

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
            # What went wrong? message!
            return render_template("token.html",
                    rfid_model=rfid_model,
                    form=rfid_change_form,
                    oppleoconfig=oppleoConfig,
                    errorlist=rfid_change_form.translateErrors(RfidChangeForm.DUTCH)
                )        
        return render_template("token.html",
                    rfid_model=rfid_model,
                    form=rfid_change_form,
                    oppleoconfig=oppleoConfig
                )       
    # JSON 
    if (request.method == 'DELETE'):
        if (token == None):
            # Not found
            abort(HTTP_CODE_404_NOT_FOUND)
        # Specific token
        rfid_model = RfidModel().get_one(token)
        # Only allow deletion if token has no charge sessions
        charge_sessions_for_rfid = ChargeSessionModel.get_charge_session_count_for_rfid(rfid_model.rfid)
        if charge_sessions_for_rfid > 0:
            # Not allowed - abort(405)
            return json.dumps({
                'success': False, 
                'token': token, 
                'reason': 'Token has {} charge sessions.'.format(charge_sessions_for_rfid)
                }), 405, {'ContentType':'application/json'} 
        rfid_model.delete()
        # 204 leads to no data in the response
        return json.dumps({'success': True, 'token': token, 'status': HTTP_CODE_200_OK}), HTTP_CODE_200_OK, {'ContentType':'application/json'} 

    # JSON 
    if (request.method == 'GET'):
        # Check if token exist, if not rfid is None
        if (token == None):
            rfid_list = []
            rfid_models = RfidModel().get_all()
            for rfid_model in rfid_models:
                rfid_model.cleanupOldOAuthToken()    # Remove any expired OAuth token info
                entry = rfid_model.to_str()
                # Add wether token has charge sessions
                entry['chargeSessions'] = ChargeSessionModel.get_charge_session_count_for_rfid(rfid_model.rfid)
                rfid_list.append(entry)
            return jsonify(rfid_list)
        # Specific token
        rfid_model = RfidModel().get_one(token)    
        if (rfid_model == None):
            return jsonify({})
        rfid_model.cleanupOldOAuthToken()    # Remove any expired OAuth token info
        return jsonify(rfid_model.to_str())

    # Not allowed
    abort(405)


# Always returns json
@flaskRoutes.route("/rfid_tokens/<path:token>/TeslaAPI/GenerateOAuth", methods=["POST"])
@flaskRoutes.route("/rfid_tokens/<path:token>/TeslaAPI/GenerateOAuth/", methods=["POST"])
@authenticated_resource  # CSRF Token is valid
def TeslaApi_GenerateOAuth(token=None):
    global flaskRoutesLogger
    flaskRoutesLogger.debug('/rfid_tokens/{}/TeslaAPI/GenerateOAuth {}'.format(token, request.method))
    flaskRoutesLogger.debug('/rfid_tokens/{}/TeslaAPI/GenerateOAuth method: {} token: {}'.format(token, request.method, token))
    rfid_model = RfidModel().get_one(token)
    if ((token == None) or (rfid_model == None)):
        # Nope, no token
        return jsonify({
            'status': HTTP_CODE_404_NOT_FOUND, 
            'reason': 'No known RFID token'
            })

    # Update for specific token
    tesla_api = TeslaAPI()
    if tesla_api.authenticate_v3(
        email=request.form['oauth_email'], 
        password=request.form['oauth_password']):
        # Obtained token
        UpdateOdometerTeslaUtil.copy_token_from_api_to_rfid_model(tesla_api, rfid_model)
        rfid_model.save()
        return jsonify({
            'status': HTTP_CODE_200_OK, 
            'token_type': rfid_model.api_token_type, 
            'created_at': rfid_model.api_created_at, 
            'expires_in': rfid_model.api_expires_in,
            'vehicles' : tesla_api.getVehicleNameIdList()
            })
    else:
        # Nope, no token
        return jsonify({
            'status': HTTP_CODE_401_UNAUTHORIZED,  
            'reason': 'Not authorized'
            })

# Always returns json
@flaskRoutes.route("/rfid_tokens/<path:token>/TeslaAPI/RefreshOAuth", methods=["POST"])
@flaskRoutes.route("/rfid_tokens/<path:token>/TeslaAPI/RefreshOAuth/", methods=["POST"])
@authenticated_resource
def TeslaApi_RefreshOAuth(token=None):
    global flaskRoutesLogger
    flaskRoutesLogger.debug('/rfid_tokens/{}/TeslaAPI/RefreshOAuth {}'.format(token, request.method))
    flaskRoutesLogger.debug('/rfid_tokens/{}/TeslaAPI/RefreshOAuth method: {} token: {}'.format(token, request.method, token))
    rfid_model = RfidModel().get_one(token)
    if ((token == None) or (rfid_model == None)):
        # Nope, no token
        return jsonify({
            'status': HTTP_CODE_404_NOT_FOUND, 
            'reason': 'No known RFID token'
            })
    # Update for specific token
    tesla_api = TeslaAPI()
    UpdateOdometerTeslaUtil.copy_token_from_rfid_model_to_api(rfid_model, tesla_api)
    if not tesla_api.refreshToken():
        return jsonify({
            'status': HTTP_CODE_500_INTERNAL_SERVER_ERROR,
            'reason': 'Refresh failed'
            })
    # Refresh succeeded, Obtained token
    UpdateOdometerTeslaUtil.copy_token_from_api_to_rfid_model(tesla_api, rfid_model)
    rfid_model.save()

    return jsonify({
        'status': HTTP_CODE_200_OK, 
        'token_type': rfid_model.api_token_type, 
        'created_at': rfid_model.api_created_at, 
        'expires_in': rfid_model.api_expires_in,
        'vehicles' : tesla_api.getVehicleNameIdList()
        })

# Always returns json
@flaskRoutes.route("/rfid_tokens/<path:token>/TeslaAPI/RevokeOAuth", methods=["POST"])
@flaskRoutes.route("/rfid_tokens/<path:token>/TeslaAPI/RevokeOAuth/", methods=["POST"])
@authenticated_resource
def TeslaApi_RevokeOAuth(token=None):
    global flaskRoutesLogger
    flaskRoutesLogger.debug('/rfid_tokens/{}/TeslaAPI/RevokeOAuth {}'.format(token, request.method))
    flaskRoutesLogger.debug('/rfid_tokens/{}/TeslaAPI/RevokeOAuth method: {} token: {}'.format(token, request.method, token))
    rfid_model = RfidModel().get_one(token)
    if ((token == None) or (rfid_model == None)):
        # Nope, no token
        return jsonify({
            'status': HTTP_CODE_404_NOT_FOUND, 
            'reason': 'No known RFID token'
            })
    # Update for specific token
    tesla_api = TeslaAPI()
    UpdateOdometerTeslaUtil.copy_token_from_rfid_model_to_api(rfid_model, tesla_api)
    if not tesla_api.revokeToken():
        return jsonify({
            'status': HTTP_CODE_500_INTERNAL_SERVER_ERROR,
            'reason': 'Revoke failed'
            })
    # Revoke succeeded, remove token
    UpdateOdometerTeslaUtil.clean_token_rfid_model(rfid_model)
    rfid_model.vehicle_vin = None
    rfid_model.save()

    return jsonify({
        'status': HTTP_CODE_200_OK, 
        'token_type': '', 
        'created_at': '', 
        'expires_in': '',
        'vehicles' : ''
        })


# Always returns json
@flaskRoutes.route("/update_settings/<path:param>", defaults={'value': None}, strict_slashes=False, methods=["POST"])
@flaskRoutes.route("/update_settings/<path:param>/<path:value>", methods=["POST"])
@flaskRoutes.route("/update_settings/<path:param>/<path:value>/", methods=["POST"])
@authenticated_resource  # CSRF Token is valid
def update_settings(param=None, value=None):

    # cannot submit / in value in the URI, verify with body
    if request.method == 'POST':
        if param != request.form.get('param'):
            param = request.form.get('param')
        if value != request.form.get('value'):
            value = request.form.get('value')

    # The USB port for the modbus interface
    if param == 'port_name':
        edm = EnergyDeviceModel.get()
        if value != edm.port_name:
            edm.port_name = value
            edm.save()
            oppleoConfig.restartRequired = True
            return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': edm.port_name })
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'reason': 'No change.' })

    # The kWhh meter modbus register parameters
    if param == 'modbusConfig':
        edm = EnergyDeviceModel.get()
        if value != edm.modbus_config:
            edm.modbus_config = value
            edm.save()
            oppleoConfig.restartRequired = True
            return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': edm.modbus_config })
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'reason': 'No change.' })

    # Enable/ disable the modbus interface
    if param == 'energyDeviceEnabled':
        edm = EnergyDeviceModel.get()
        edm.device_enabled = True if value.lower() in ['true', '1', 't', 'y', 'yes'] else False
        edm.save()
        if oppleoConfig.energyDevice is not None:
            oppleoConfig.energyDevice.enable( edm.device_enabled )
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': edm.port_name })

    # With an open charge session, there params are not allowed to change
    if param in ['chargerName', 'chargerTariff'] and \
       ChargeSessionModel.has_open_charge_session_for_device(oppleoConfig.chargerName):
        return jsonify({ 'status': 409, 'param': param, 'reason': 'Er is een laadsessie actief.' })


    if (param == 'offpeakEnabled'):
        oppleoConfig.offpeakEnabled = True if value.lower() in ['true', '1', 't', 'y', 'yes'] else False
        ophm = OffPeakHoursModel()
        WebSocketUtil.emit(
                wsEmitQueue=oppleoConfig.wsEmitQueue,
                event='off_peak_status_update', 
                id=oppleoConfig.chargerName,
                data={ 'isOffPeak': ophm.is_off_peak_now(),
                       'offPeakEnabled': oppleoConfig.offpeakEnabled,
                       'peakAllowOnePeriod': oppleoConfig.allowPeakOnePeriod
                },
                namespace='/charge_session',
                public=True
                )
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': oppleoConfig.offpeakEnabled })

    if (param == 'allowPeakOnePeriod'):
        oppleoConfig.allowPeakOnePeriod = True if value.lower() in ['true', '1', 't', 'y', 'yes'] else False
        ophm = OffPeakHoursModel()
        WebSocketUtil.emit(
                event='off_peak_status_update', 
                    id=oppleoConfig.chargerName,
                    data={ 'isOffPeak': ophm.is_off_peak_now(),
                           'offPeakEnabled': oppleoConfig.offpeakEnabled,
                           'peakAllowOnePeriod': oppleoConfig.allowPeakOnePeriod
                    },
                    namespace='/charge_session',
                    public=True
                )
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': oppleoConfig.allowPeakOnePeriod })

    if (param == 'autoSessionEnabled'):
        oppleoConfig.autoSessionEnabled = True if value.lower() in ['true', '1', 't', 'y', 'yes'] else False
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': oppleoConfig.autoSessionEnabled })

    if (param == 'autoSessionCondenseSameOdometer'):
        oppleoConfig.autoSessionCondenseSameOdometer = True if value.lower() in ['true', '1', 't', 'y', 'yes'] else False
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': oppleoConfig.autoSessionCondenseSameOdometer })

    # Add off peak database entry day|month|year|recurring|description (month is zero-based)
    if (param == 'offPeakAddHolidayEntry'):
        vAr = value.split('|')
        ophm = OffPeakHoursModel()
        ophm.holiday_day = vAr.pop(0)
        ophm.holiday_month = vAr.pop(0) # js is 0-based, python/db is 1-based - translated before submit
        ophm.holiday_year = vAr.pop(0)
        ophm.recurring = True if vAr.pop(0).lower() in ['true', 1] else False
        ophm.description = unquote(vAr.pop(0))
        ophm.off_peak_start = '00:00:00'
        ophm.off_peak_end = '23:59:00'
        ophm.is_holiday = True
        # Save
        ophm.save()
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': str(ophm.id) })

    # Delete off peak database entry
    if (param == 'offPeakDeleteEntry') and (isinstance(value, int) or RepresentsInt(value)):
        # Delete
        OffPeakHoursModel.deleteId(value)
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': value })

    # chargerName
    if (param == 'chargerName') and isinstance(value, str) and len(value) > 0:
        oppleoConfig.chargerName = value
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': value })

    # factorWhkm
    if (param == 'factorWhkm') and (isinstance(value, int) or RepresentsInt(value)):
        oppleoConfig.factorWhkm = int(value)
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': value })

    # chargerTariff
    if (param == 'chargerTariff') and (isinstance(value, float) or RepresentsFloat(value)):
        oppleoConfig.chargerTariff = float(value)
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': value })

    # Enable/ disable the RFID Reader via SPI on the GPIO
    if (param == 'rfidEnabled') and isinstance(value, str):
        oppleoSystemConfig.rfidEnabled = True if value.lower() in ['true', '1', 't', 'y', 'yes'] else False
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': value })

    # gpioMode
    if (param == 'gpioMode') and (isinstance(value, int) or RepresentsInt(value)):
        oppleoConfig.gpioMode = int(value)
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': value })

    # Enable/ disable the oppleo LED via GPIO
    if (param == 'oppleoLedEnabled') and isinstance(value, str):
        oppleoSystemConfig.oppleoLedEnabled = True if value.lower() in ['true', '1', 't', 'y', 'yes'] else False
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': value })

    # pinLedRed
    if (param == 'pinLedRed') and (isinstance(value, int) or RepresentsInt(value)):
        oppleoConfig.pinLedRed = int(value)
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': value })

    # pinLedGreen
    if (param == 'pinLedGreen') and (isinstance(value, int) or RepresentsInt(value)):
        oppleoConfig.pinLedGreen = int(value)
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': value })

    # pinLedBlue
    if (param == 'pinLedBlue') and (isinstance(value, int) or RepresentsInt(value)):
        oppleoConfig.pinLedBlue = int(value)
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': value })

    # Enable/ disable the oppleo buzzer via GPIO
    if (param == 'buzzerEnabled') and isinstance(value, str):
        oppleoSystemConfig.buzzerEnabled = True if value.lower() in ['true', '1', 't', 'y', 'yes'] else False
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': value })

    # pinBuzzer
    if (param == 'pinBuzzer') and (isinstance(value, int) or RepresentsInt(value)):
        oppleoConfig.pinBuzzer = int(value)
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': value })

    # Enable/ disable the EVSE Switch via GPIO
    if (param == 'evseSwitchEnabled') and isinstance(value, str):
        oppleoSystemConfig.evseSwitchEnabled = True if value.lower() in ['true', '1', 't', 'y', 'yes'] else False
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': value })

    # pinEvseSwitch
    if (param == 'pinEvseSwitch') and (isinstance(value, int) or RepresentsInt(value)):
        oppleoConfig.pinEvseSwitch = int(value)
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': value })

    # Enable/ disable the EVSE Led Reader via GPIO
    if (param == 'evseLedReaderEnabled') and isinstance(value, str):
        oppleoSystemConfig.evseLedReaderEnabled = True if value.lower() in ['true', '1', 't', 'y', 'yes'] else False
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': value })

    # pinEvseLed
    if (param == 'pinEvseLed') and (isinstance(value, int) or RepresentsInt(value)):
        oppleoConfig.pinEvseLed = int(value)
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': value })

    # DATABASE_URL
    validation="^(postgresql://)[a-zA-Z0-9]+(:)[a-zA-Z0-9]+(@)[a-zA-Z0-9.:/]+$"
    if (param == 'DATABASE_URL') and isinstance(value, str) and re.match(validation, value):
        oppleoSystemConfig.DATABASE_URL = value
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': value })

    # pulseLedMin
    if (param == 'pulseLedMin') and (isinstance(value, int) or RepresentsInt(value)):
        oppleoConfig.pulseLedMin = int(value)
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': value })

    # pulseLedMax
    if (param == 'pulseLedMax') and (isinstance(value, int) or RepresentsInt(value)):
        oppleoConfig.pulseLedMax = int(value)
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': value })

    # autoSessionMinutes
    if (param == 'autoSessionMinutes') and (isinstance(value, int) or RepresentsInt(value)):
        oppleoConfig.autoSessionMinutes = int(value)
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': value })

    # autoSessionEnergy
    if (param == 'autoSessionEnergy') and (isinstance(value, float) or RepresentsFloat(value)):
        oppleoConfig.autoSessionEnergy = int(value)
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': value })

    # logFile
    if (param == 'logFile') and isinstance(value, str) and len(value) > 0:
        oppleoSystemConfig.logFile = value
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': value })

    # logLevel
    if (param == 'logLevel') and isinstance(value, str) and len(value) > 0:
        oppleoSystemConfig.logLevel = value
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': value })

    # logMaxBytes
    validation=r'^[1-9]\d*$'
    if (param == 'logMaxBytes') and isinstance(value, str) and re.match(validation, value):
        try:
            value = int(value)
        except ValueError as e:
            # Conditions not met
            return jsonify({ 'status': HTTP_CODE_400_BAD_REQUEST, 'param': param, 'reason': 'No valid integer value' })
        oppleoSystemConfig.logMaxBytes = value
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': value })

    # logBackupCount
    validation=r'^\d*$'
    if (param == 'logBackupCount') and isinstance(value, str) and re.match(validation, value):
        try:
            value = int(value)
        except ValueError as e:
            # Conditions not met
            return jsonify({ 'status': HTTP_CODE_400_BAD_REQUEST, 'param': param, 'reason': 'No valid integer value' })
        oppleoSystemConfig.logBackupCount = value
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': value })

    # Python path
    if (param == 'PYTHONPATH') and isinstance(value, str):
        oppleoSystemConfig.PYTHONPATH = value
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': value })

    # onDbFailureAllowRestart
    if (param == 'onDbFailureAllowRestart') and isinstance(value, str):
        oppleoSystemConfig.onDbFailureAllowRestart = True if value.lower() in ['true', '1', 't', 'y', 'yes'] else False
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': value })

    # onDbFailureMagicPassword
    if (param == 'onDbFailureMagicPassword') and isinstance(value, str):
        oppleoSystemConfig.onDbFailureMagicPassword = value
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': value })

    # onDbFailureAllowUrlChange
    if (param == 'onDbFailureAllowUrlChange') and isinstance(value, str):
        oppleoSystemConfig.onDbFailureAllowUrlChange = True if value.lower() in ['true', '1', 't', 'y', 'yes'] else False
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': value })

    # onDbFailureShowCurrentUrl
    if (param == 'onDbFailureShowCurrentUrl') and isinstance(value, str):
        oppleoSystemConfig.onDbFailureShowCurrentUrl = True if value.lower() in ['true', '1', 't', 'y', 'yes'] else False
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': value })

    # baudrate
    if (param == 'baudrate') and int(value) in [2400, 4800, 9600, 19200, 38400, 57600, 115200]:
        energyDeviceModel = EnergyDeviceModel.get()
        energyDeviceModel.baudrate = value
        energyDeviceModel.save()
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': value })

    # slave_address
    validation="^([01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])$"
    if (param == 'slave_address') and isinstance(value, str) and re.match(validation, value):
        try:
            value = int(value)
        except ValueError as e:
            # Conditions not met
            return jsonify({ 'status': HTTP_CODE_400_BAD_REQUEST, 'param': param, 'reason': 'No valid integer value' })
        energyDeviceModel = EnergyDeviceModel.get()
        energyDeviceModel.slave_address = value
        energyDeviceModel.save()
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': value })

    # prowlEnabled
    if (param == 'prowlEnabled'):
        oppleoSystemConfig.prowlEnabled = True if value.lower() in ['true', '1', 't', 'y', 'yes'] else False
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': oppleoSystemConfig.prowlEnabled })

    # prowlApiKey
    if (param == 'prowlApiKey') and isinstance(value, str):
        oppleoSystemConfig.prowlApiKey = value if len(value) > 0 else None
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': value })

    # webChargeOnDashboard
    if (param == 'webChargeOnDashboard'):
        oppleoConfig.webChargeOnDashboard = True if value.lower() in ['true', '1', 't', 'y', 'yes'] else False
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': oppleoConfig.webChargeOnDashboard })

    # authWebCharge
    if (param == 'authWebCharge'):
        oppleoConfig.authWebCharge = True if value.lower() in ['true', '1', 't', 'y', 'yes'] else False
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': oppleoConfig.authWebCharge })

    # restrictDashboardAccess
    if (param == 'restrictDashboardAccess'):
        oppleoConfig.restrictDashboardAccess = True if value.lower() in ['true', '1', 't', 'y', 'yes'] else False
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': oppleoConfig.restrictDashboardAccess })

    # restrictMenu
    if (param == 'restrictMenu'):
        oppleoConfig.restrictMenu = True if value.lower() in ['true', '1', 't', 'y', 'yes'] else False
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': oppleoConfig.restrictMenu })

    # allowLocalDashboardAccess
    if (param == 'allowLocalDashboardAccess'):
        oppleoConfig.allowLocalDashboardAccess = True if value.lower() in ['true', '1', 't', 'y', 'yes'] else False
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': oppleoConfig.allowLocalDashboardAccess })

    # routerIPAddress
    validation="^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.|$)){4}$"
    if (param == 'routerIPAddress') and isinstance(value, str) and re.match(validation, value):
        oppleoConfig.routerIPAddress = value
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': value })

    # receiptPrefix
    validation="^[A-Za-z0-9.-]{0,20}$"
    if (param == 'receiptPrefix') and isinstance(value, str) and re.match(validation, value):
        oppleoConfig.receiptPrefix = value
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': value })

    # modbusInterval
    validation="^([1-9]|[1-5][0-9]|60)$"
    if (param == 'modbusInterval') and isinstance(value, str) and re.match(validation, value):
        try:
            value = int(value)
        except ValueError as e:
            # Conditions not met
            return jsonify({ 'status': HTTP_CODE_404_NOT_FOUND, 'param': param, 'reason': 'No valid integer value' })
        oppleoConfig.modbusInterval = value
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': value })

    # httpPort
    validation="^([0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])$"
    if (param == 'httpPort') and isinstance(value, str) and re.match(validation, value):
        oppleoSystemConfig.httpPort = value
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': oppleoSystemConfig.httpPort })

    # httpTimeout 0-999
    validation="^[1-9][0-9]{0,2}$"
    if (param == 'httpTimeout') and isinstance(value, str) and re.match(validation, value):
        oppleoSystemConfig.httpTimeout = value
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': oppleoSystemConfig.httpTimeout })

    # backupEnabled
    if (param == 'backupEnabled'):
        backupUtil = BackupUtil()
        # Make sure the thread running and the config settings are in sync
        backupUtil.lock.acquire()
        enableBackup = True if value.lower() in ['true', '1', 't', 'y', 'yes'] else False
        oppleoConfig.backupEnabled = enableBackup
        if enableBackup:
            BackupUtil().startBackupMonitorThread()
        else:
            BackupUtil().stopBackupMonitorThread()
        backupUtil.lock.release()

        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': oppleoConfig.backupEnabled })

    # backupInterval
    if ((param == 'backupInterval') and isinstance(value, str) and 
        (value == oppleoConfig.BACKUP_INTERVAL_WEEKDAY or value == oppleoConfig.BACKUP_INTERVAL_CALDAY) ):
        oppleoConfig.backupInterval = value
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': value })

    # backupIntervalWeekday
    if (param == 'backupIntervalWeekday'):
        try:
            lst = json.loads(value)
            if len(lst) == 7 and all(isinstance(x, bool) for x in lst):
                oppleoConfig.backupIntervalWeekday = json.dumps(lst)
                return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': value })
        except Exception as e:
            pass
        return jsonify({ 'status': HTTP_CODE_400_BAD_REQUEST, 'param': param, 'value': value })

    # backupIntervalWeekday
    if (param == 'backupIntervalCalday'):
        try:
            lst = json.loads(value)
            if len(lst) == 32:
                # List is 1 offset, make 0 offset by popping the first entry
                lst.pop(0)
            if len(lst) == 31 and all(isinstance(x, bool) for x in lst):
                oppleoConfig.backupIntervalCalday = json.dumps(lst)
                return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': value })
        except Exception as e:
            pass
        return jsonify({ 'status': HTTP_CODE_400_BAD_REQUEST, 'param': param, 'value': value })

    # backupTimeOfDay
    validation='^([01]\d|2[0-3]):?([0-5]\d)$'
    if (param == 'backupTimeOfDay') and isinstance(value, str) and re.match(validation, value):
        oppleoConfig.backupTimeOfDay = time(hour=int(value[0:2]), minute=int(value[3:5]), second=0, microsecond=0)
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': value })

    # backupLocalHistory
    validation="^(0?[1-9]|[1-9][0-9])$"
    if (param == 'backupLocalHistory') and isinstance(value, str) and re.match(validation, value):
        try:
            value = int(value)
        except ValueError as e:
            # Conditions not met
            return jsonify({ 'status': HTTP_CODE_404_NOT_FOUND, 'param': param, 'reason': 'No valid integer value' })
        oppleoConfig.backupLocalHistory = value
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': value })

    # osBackupEnabled
    if (param == 'osBackupEnabled'):
        enableOsBackup = True if value.lower() in ['true', '1', 't', 'y', 'yes'] else False
        # Only enable if valid settings
        if enableOsBackup and not BackupUtil().validOffsiteBackup():
            return jsonify({ 'status': HTTP_CODE_405_METHOD_NOT_ALLOWED, 'param': param, 'value': oppleoConfig.osBackupEnabled })
        oppleoConfig.osBackupEnabled = enableOsBackup
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': oppleoConfig.osBackupEnabled })

    # osBackupType
    if (param == 'osBackupType') and isinstance(value, str) and value.lower() in ['smb']:
        oppleoConfig.osBackupType = value
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': value })

    # osBackupHistory
    validation="^(0?[1-9]|[1-9][0-9])$"
    if (param == 'osBackupHistory') and isinstance(value, str) and re.match(validation, value):
        try:
            value = int(value)
        except ValueError as e:
            # Conditions not met
            return jsonify({ 'status': HTTP_CODE_404_NOT_FOUND, 'param': param, 'reason': 'No valid integer value' })
        oppleoConfig.osBackupHistory = value
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': value })

    # smbBackupSettings
    if (param == 'smbBackupSettings'):
        try:
            jsonD = json.loads(value)
        except JSONDecodeError as jde:
            return jsonify({ 'status': HTTP_CODE_400_BAD_REQUEST, 'param': param, 'value': value, 'reason' : 'JSON decode error' })

        # Check if the keys do exist in the jsonD dict, fail 400 if they don't
        if not all([True for key in ['serverOrIP', 'username', 'password', 'serviceName', 'remotePath'] if key in jsonD.keys()]):
            # Not all required parameters
            return jsonify({ 'status': HTTP_CODE_400_BAD_REQUEST, 'param': param, 'value': value, 'reason' : 'Missing variables' })

        if 'osBackupType' in jsonD.keys():
            oppleoConfig.osBackupType = jsonD['osBackupType']

        oppleoConfig.smbBackupServerNameOrIPAddress = jsonD['serverOrIP']
        oppleoConfig.smbBackupUsername              = jsonD['username']
        oppleoConfig.smbBackupPassword              = jsonD['password']
        oppleoConfig.smbBackupServiceName           = jsonD['serviceName']
        oppleoConfig.smbBackupRemotePath            = jsonD['remotePath']
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': value })

    # smbBackupIPAddress (can be empty)
    validation="^()|((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.|$)){4}$"
    if (param == 'smbBackupIPAddress') and isinstance(value, str) and re.match(validation, value):
        oppleoConfig.smbBackupIPAddress = value
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': value })

    # smbBackupUsername
    if (param == 'smbBackupUsername') and isinstance(value, str):
        oppleoConfig.smbBackupUsername = value
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': value })

    # smbBackupPassword
    if (param == 'smbBackupPassword') and isinstance(value, str):
        oppleoConfig.smbBackupPassword = value
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': value })

    # smbBackupShareName
    if (param == 'smbBackupShareName') and isinstance(value, str):
        oppleoConfig.smbBackupShareName = value
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': value })

    # smbBackupSharePath
    if (param == 'smbBackupSharePath') and isinstance(value, str):
        oppleoConfig.smbBackupSharePath = value
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': value })

    # vehicleDataOnDashboard
    if (param == 'vehicleDataOnDashboard'):
        oppleoConfig.vehicleDataOnDashboard = True if value.lower() in ['true', '1', 't', 'y', 'yes'] else False
        if not oppleoConfig.vehicleDataOnDashboard:
            WebSocketUtil.emit(
                wsEmitQueue=oppleoConfig.wsEmitQueue,
                event='vehicle_charge_status_stopped', 
                id=oppleoConfig.chargerName,
                namespace='/charge_session',
                public=False
                )

        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': oppleoConfig.vehicleDataOnDashboard })

    # No parameter found or conditions not met
    return jsonify({ 'status': HTTP_CODE_404_NOT_FOUND, 'param': param, 'reason': 'Not found' })



# Always returns json
@flaskRoutes.route("/backup/<path:cmd>", defaults={'value': None}, strict_slashes=False, methods=["GET"])
@flaskRoutes.route("/backup/<path:cmd>/<path:data>", methods=["GET"])
@flaskRoutes.route("/backup/<path:cmd>/<path:data>/", methods=["GET"])
@authenticated_resource  # CSRF Token is valid
def getBackupInfo(cmd=None, data=None):
    global flaskRoutesLogger, oppleoConfig
    flaskRoutesLogger.debug('/backup/{}'.format(cmd))

    backupUtil = BackupUtil()
    
    if isinstance(cmd, str) and len(cmd) > 3:
        if (cmd.lower() == "smbvalidateaccount"):
            # Return the shared folders
            # Check if valid JSON, fail 400 if not
            try:
                jsonD = json.loads(data)
            except JSONDecodeError as jde:
                return jsonify({ 
                    'status'            : HTTP_CODE_400_BAD_REQUEST,
                    'cmd'               : cmd,
                    'result'            : 'false',
                    'reason'            : jde.msg
                    })                

            # Check if the keys do exist in the jsonD dict, fail 400 if they don't
            if not all([True for key in ['serverOrIP', 'username', 'password'] if key in jsonD.keys()]):
                # Not all required parameters
                return jsonify({ 
                    'status'            : HTTP_CODE_400_BAD_REQUEST,
                    'cmd'               : cmd,
                    'result'            : 'false',
                    'reason'            : 'Missing variables'
                    })                

            validConnection, connectionDetails = backupUtil.validateSMBAccount(serverOrIP=jsonD['serverOrIP'],
                                                                               username=jsonD['username'],
                                                                               password=jsonD['password']
                                                                              )
            return jsonify({ 
                'status'            : HTTP_CODE_200_OK,
                'cmd'               : cmd,
                'validConnection'   : validConnection,
                'resolved'          : connectionDetails['resolved'],
                'connectionRefused' : connectionDetails['connectionRefused']
                })

        if (cmd.lower() == "smblistservices"):
            # Return the shared folders
            # Check if valid JSON, fail 400 if not
            try:
                jsonD = json.loads(data)
            except JSONDecodeError as jde:
                return jsonify({ 
                    'status'            : HTTP_CODE_400_BAD_REQUEST,
                    'cmd'               : cmd,
                    'result'            : 'false',
                    'reason'            : jde.msg
                    })                

            # Check if the keys do exist in the jsonD dict, fail 400 if they don't
            if not all([True for key in ['serverOrIP', 'username', 'password'] if key in jsonD.keys()]):
                # Not all required parameters
                return jsonify({ 
                    'status'            : HTTP_CODE_400_BAD_REQUEST,
                    'cmd'               : cmd,
                    'result'            : 'false',
                    'reason'            : 'Missing variables'
                    })                

            shareList, connectionDetails = backupUtil.listSMBShares(serverOrIP=jsonD['serverOrIP'],
                                                                    username=jsonD['username'],
                                                                    password=jsonD['password']
                                                                    )

            return jsonify({ 
                'status'            : HTTP_CODE_200_OK,
                'cmd'               : cmd,
                'shareList'         : shareList if isinstance(shareList, list) else [],
                'resolved'          : connectionDetails['resolved'],
                'connectionRefused' : connectionDetails['connectionRefused'],
                'validConnection'   : connectionDetails['validConnection']
                })

        if (cmd.lower() == "smblistdirectories"):
            # Return the shared folders
            # Check if valid JSON, fail 400 if not
            try:
                jsonD = json.loads(data)
            except JSONDecodeError as jde:
                return jsonify({ 
                    'status'            : HTTP_CODE_400_BAD_REQUEST,
                    'cmd'               : cmd,
                    'result'            : 'false',
                    'reason'            : jde.msg
                    })                

            # Check if the keys do exist in the jsonD dict, fail 400 if they don't
            if not all([True for key in ['serverOrIP', 'username', 'password', 'serviceName', 'smbPath' ] if key in jsonD.keys()]):
                # Not all required parameters
                return jsonify({ 
                    'status'            : HTTP_CODE_400_BAD_REQUEST,
                    'cmd'               : cmd,
                    'result'            : 'false',
                    'reason'            : 'Missing variables'
                    })                

            directoryList, connectionDetails = backupUtil.listSMBFilesAndDirectories(
                            serverOrIP=jsonD['serverOrIP'],
                            username=jsonD['username'],
                            password=jsonD['password'],
                            serviceName=jsonD['serviceName'],
                            smbPath=jsonD['smbPath'],
                            hideDirectories=False,
                            hideFiles=True
                        )

            return jsonify({ 
                'status'            : HTTP_CODE_200_OK,
                'cmd'               : cmd,
                'directoryList'     : directoryList if isinstance(directoryList, list) else [],
                'resolved'          : connectionDetails['resolved'],
                'connectionRefused' : connectionDetails['connectionRefused'],
                'validConnection'   : connectionDetails['validConnection'],
                'smbPath'           : connectionDetails['smbPath']
                })

        if (cmd.lower() == "listlocalbackups"):
            backupList = backupUtil.listLocalBackups()

            return jsonify({ 
                'status'            : HTTP_CODE_200_OK,
                'cmd'               : cmd,
                'directory'         : backupList['directory'],
                'localBackupList'   : backupList['files']
                })

        if (cmd.lower() == "listoffsitebackups"):
            result = backupUtil.listOffsiteBackups()

            data = { 'status': HTTP_CODE_200_OK if result['success'] else HTTP_CODE_404_NOT_FOUND,
                     'cmd'   : cmd
                   }
            if result['success']:
                data.update({ 'directory'     : result['directory'],
                              'osBackupList'  : result['files']
                            })
            else:
                data.update({ 'reason' : result['reason'] })

            return jsonify(data)


        if (cmd.lower() == "createbackupnow"):
            backupUtil.startSingleBackupThread()
            return jsonify({ 
                'status'            : HTTP_CODE_200_OK,
                'cmd'               : cmd
                })

        if (cmd.lower() == "removelocalbackup"):
            try:
                jsonD = json.loads(data)
            except JSONDecodeError as jde:
                return jsonify({ 
                    'status'            : HTTP_CODE_400_BAD_REQUEST,
                    'cmd'               : cmd,
                    'result'            : 'false',
                    'reason'            : jde.msg
                    })                

            # Check if the keys do exist in the jsonD dict, fail 400 if they don't
            if not all([True for key in ['filename'] if key in jsonD.keys()]):
                # Not all required parameters
                return jsonify({ 
                    'status'            : HTTP_CODE_400_BAD_REQUEST,
                    'cmd'               : cmd,
                    'result'            : 'false',
                    'reason'            : 'Missing variables'
                    })                

            result = backupUtil.removeLocalBackup(filename=jsonD['filename'])
            return jsonify({ 
                'status'            : HTTP_CODE_200_OK if result['result'] else 
                                        HTTP_CODE_404_NOT_FOUND if not result['found'] else 
                                        HTTP_CODE_500_INTERNAL_SERVER_ERROR,
                'cmd'               : cmd
                })

        if (cmd.lower() == "removeoffsitebackup"):
            try:
                jsonD = json.loads(data)
            except JSONDecodeError as jde:
                return jsonify({ 
                    'status'            : HTTP_CODE_400_BAD_REQUEST,
                    'cmd'               : cmd,
                    'result'            : 'false',
                    'reason'            : jde.msg
                    })                

            # Check if the keys do exist in the jsonD dict, fail 400 if they don't
            if not all([True for key in ['filename'] if key in jsonD.keys()]):
                # Not all required parameters
                return jsonify({ 
                    'status'            : HTTP_CODE_400_BAD_REQUEST,
                    'cmd'               : cmd,
                    'result'            : 'false',
                    'reason'            : 'Missing variables'
                    })                

            result = backupUtil.removeOffsiteBackup(filename=jsonD['filename'])
            return jsonify({ 
                'status'            : HTTP_CODE_200_OK if result['result'] else 
                                        HTTP_CODE_404_NOT_FOUND if not result['found'] else 
                                        HTTP_CODE_500_INTERNAL_SERVER_ERROR,
                'cmd'               : cmd
                })


    return jsonify({ 
        'status'        : HTTP_CODE_500_INTERNAL_SERVER_ERROR, 
        'id'            : oppleoConfig.chargerName, 
        'reason'        : 'Could not return information'
        })



# Always returns json
# This function takes a long time (due to TeslaAPI being slooow) -> Just wait for the background task to 
# submit updates through websockets.
@flaskRoutes.route("/vehicle_charge_state", methods=["GET"])
@flaskRoutes.route("/vehicle_charge_state/", methods=["GET"])
@authenticated_resource  # CSRF Token is valid
def getVehicleChargeStatus():
    global flaskRoutesLogger, oppleoConfig
    
    # Only if existing charge session, with rfid with token
    openChargeSession = ChargeSessionModel.getOpenChargeSession(oppleoConfig.chargerName)
    if openChargeSession is None:
        return jsonify({ 
            'status'        : HTTP_CODE_404_NOT_FOUND, 
            'id'            : oppleoConfig.chargerName, 
            'reason'        : 'No existing charge session'
            })
    rfidTag = RfidModel.get_one(openChargeSession.rfid)
    if rfidTag is None:
        return jsonify({ 
            'status'        : HTTP_CODE_500_INTERNAL_SERVER_ERROR, 
            'id'            : oppleoConfig.chargerName, 
            'reason'        : 'No RFID for charge session'
            })
    if rfidTag.api_access_token is None:
        return jsonify({ 
            'status'        : HTTP_CODE_404_NOT_FOUND, 
            'id'            : oppleoConfig.chargerName, 
            'reason'        : 'No token for RFID'
            })
    teslaApi = TeslaAPI()
    # TODO timeout with max ~10sec wait
    tKey = tokenMediator.checkout(token=rfidTag.api_access_token, ref='flaskRoutes:'+rfidTag.rfid, wait=False)
    if tKey is None:
        # Bum out, token not valid or in use
        if not tokenMediator.validate(token=rfidTag.api_access_token):
            return jsonify({
                'status'        : HTTP_CODE_404_NOT_FOUND, 
                'id'            : oppleoConfig.chargerName,
                'reason'        : 'No token for RFID'
                })
        return jsonify({
            'status'        : HTTP_CODE_409_CONFLICT, 
            'id'            : oppleoConfig.chargerName,
            'reason'        : 'Token not available'
            })
    UpdateOdometerTeslaUtil.copy_token_from_rfid_model_to_api(rfidTag, teslaApi)
    if not teslaApi.hasValidToken():
        tokenMediator.invalidate(token=rfidTag.api_access_token, key=tKey, ref='flaskRoutes:'+rfidTag.rfid)
        return jsonify({ 
            'status'        : HTTP_CODE_404_NOT_FOUND, 
            'id'            : oppleoConfig.chargerName, 
            'reason'        : 'No token for RFID'
            })
    # Refresh if required
    if teslaApi.refreshTokenIfRequired():
        # Invalidate the old token
        tokenMediator.invalidate(token=rfidTag.api_access_token, key=tKey, ref='flaskRoutes:'+rfidTag.rfid)
        UpdateOdometerTeslaUtil.copy_token_from_api_to_rfid_model(teslaApi, rfidTag)
        # Checkout the new token
        tKey = tokenMediator.checkout(token=rfidTag.api_access_token, ref='flaskRoutes:'+rfidTag.rfid, wait=True)
        rfidTag.save()

    # Get charge state
    chargeState = teslaApi.getChargeStateWithId(rfidTag.vehicle_id)
    vehicle = teslaApi.getVehicleWithId(rfidTag.vehicle_id)
    # vehicleState = teslaApi.getVehicleStateWithId(rfidTag.vehicle_id)
    # Release the token
    tokenMediator.release(token=rfidTag.api_access_token, key=tKey)
    if chargeState is None:
        return jsonify({ 
            'status'        : HTTP_CODE_500_INTERNAL_SERVER_ERROR, 
            'id'            : oppleoConfig.chargerName, 
            'reason'        : 'No charge state obtained for charge session'
            })

    formattedChargeState = formatChargeState(chargeState)
    formattedVehicle = formatVehicle(vehicle)
    # we got it, share it
    if len(oppleoConfig.connectedClients) > 1:
        WebSocketUtil.emit(
            wsEmitQueue=oppleoConfig.wsEmitQueue,
            event='vehicle_charge_status_update', 
            id=oppleoConfig.chargerName,
            data={ 'chargeState'            : formattedChargeState,
                   'vehicle'                : formattedVehicle,
                   'vehicleMonitorInterval' : str(oppleoConfig.vcsmThread.vehicleMonitorInterval if oppleoConfig.vcsmThread is not None else -1)
            },
            namespace='/charge_session',
            public=True
            )

    return jsonify({ 
        'status'                    : HTTP_CODE_200_OK, 
        'id'                        : oppleoConfig.chargerName,
        'chargeState'               : formattedChargeState,
        'vehicle'                   : formattedVehicle,
        'vehicleMonitorInterval'    : str(oppleoConfig.vcsmThread.vehicleMonitorInterval if oppleoConfig.vcsmThread is not None else -1)
        })



# Always returns json
@flaskRoutes.route("/system_status/", methods=["GET"])
@authenticated_resource
def systemStatus():
    global flaskRoutesLogger, oppleoConfig
    flaskRoutesLogger.debug('/system_status/')

    return jsonify({
        'status': HTTP_CODE_200_OK, 
        'restartRequired': (oppleoConfig.restartRequired or oppleoSystemConfig.restartRequired),
        'softwareUpdateInProgress': oppleoConfig.softwareUpdateInProgress,
        'startTime': oppleoConfig.upSinceDatetimeStr,
        'backupInProgress' : BackupUtil().backupInProgress
        })


# Always returns json
@flaskRoutes.route("/software_status/", methods=["GET"])
@authenticated_resource
def softwareStatus():
    global flaskRoutesLogger, oppleoConfig
    flaskRoutesLogger.debug('/software_status/')

    # Update status from github
    GitUtil.gitRemoteUpdate()

    return jsonify({
        'status': HTTP_CODE_200_OK, 
        'softwareUpdateAvailable': GitUtil.gitUpdateAvailable(),
        'availableSoftwareDate': GitUtil.lastRemoteMasterGitDateStr()
        })

