from crypt import methods
from operator import indexOf
import os
import threading
from datetime import datetime, time
from flask import Flask, Blueprint, render_template, abort, request, url_for, redirect, jsonify, session, send_file
from flask import current_app as app # Note: that the current_app proxy is only available in the context of a request.

from jinja2.exceptions import TemplateNotFound
import requests
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from functools import wraps
import json
from json import JSONDecodeError

import logging
import re
from urllib.parse import urlparse, unquote
import io
import uuid
import validators

from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask_socketio import SocketIO, emit

from nl.oppleo.config.OppleoConfig import oppleoConfig
from nl.oppleo.config.OppleoSystemConfig import oppleoSystemConfig
from nl.oppleo.config.ChangeLog import changeLog
from nl.oppleo.daemon.MqttSendHistoryThread import MqttSendHistoryThread, MqttSendHistoryThreadMode

from nl.oppleo.exceptions.Exceptions import (NotAuthorizedException, 
                                             ExpiredException)

from nl.oppleo.models.User import User
from nl.oppleo.webapp.AuthorizeForm import AuthorizeForm
from nl.oppleo.models.EnergyDeviceMeasureModel import EnergyDeviceMeasureModel
from nl.oppleo.models.Raspberry import Raspberry
from nl.oppleo.models.ChargeSessionModel import ChargeSessionModel
from nl.oppleo.models.RfidModel import RfidModel
from nl.oppleo.models.ChargerConfigModel import ChargerConfigModel
from nl.oppleo.models.ChargeSessionModel import ChargeSessionModel
from nl.oppleo.models.EnergyDeviceModel import EnergyDeviceModel
from nl.oppleo.models.OffPeakHoursModel import OffPeakHoursModel
from nl.oppleo.webapp.RfidChangeForm import RfidChangeForm
from nl.oppleo.api.VehicleApi import VehicleApi
from nl.oppleo.utils.UpdateOdometerTeslaUtil import UpdateOdometerTeslaUtil
from nl.oppleo.services.Evse import Evse
from nl.oppleo.utils.OutboundEvent import OutboundEvent
from nl.oppleo.utils.GitUtil import GitUtil
from nl.oppleo.utils.Authenticator import (keyUri, makeQR, generateTotpSharedSecret, encryptAES, decryptAES, validateTotp)
from nl.oppleo.utils.IPv4 import IPv4

from nl.oppleo.utils.EnergyModbusReader import modbusConfigOptions
from nl.oppleo.utils.BackupUtil import BackupUtil

from nl.oppleo.utils.TokenMediator import tokenMediator

from nl.oppleo.daemon.MqttSendHistoryThread import Status as mhtsStatus


# https://en.wikipedia.org/wiki/List_of_HTTP_status_codes
HTTP_CODE_200_OK                    = 200
HTTP_CODE_202_ACCEPTED              = 202  # Accepted, processing pending
HTTP_CODE_303_SEE_OTHER             = 303  # Conflict, POST on existing resource
HTTP_CODE_400_BAD_REQUEST           = 400
HTTP_CODE_401_UNAUTHORIZED          = 401
HTTP_CODE_403_FORBIDDEN             = 403
HTTP_CODE_404_NOT_FOUND             = 404
HTTP_CODE_405_METHOD_NOT_ALLOWED    = 405
HTTP_CODE_409_CONFLICT              = 409
HTTP_CODE_410_GONE                  = 410
HTTP_CODE_424_FAILED_DEPENDENCY     = 424
HTTP_CODE_500_INTERNAL_SERVER_ERROR = 500
HTTP_CODE_501_NOT_IMPLEMENTED       = 501

DETAIL_CODE_20_2FA_NOT_ENABLED                      =  20    # HTTP_CODE_400_BAD_REQUEST
DETAIL_CODE_21_2FA_ENABLED                          =  21    # HTTP_CODE_400_BAD_REQUEST
DETAIL_CODE_23_2FA_CODE_INCORRECT                   =  23    # HTTP_CODE_400_BAD_REQUEST
DETAIL_CODE_25_PASSWORD_INCORRECT                   =  25    # HTTP_CODE_401_UNAUTHORIZED
# Security threat to leak this information
DETAIL_CODE_26_USERNAME_UNKNOWN                     =  26    # HTTP_CODE_401_UNAUTHORIZED
DETAIL_CODE_28_ACTION_UNKNOWN                       =  28    # HTTP_CODE_400_BAD_REQUEST
DETAIL_CODE_29_PROCESS_STEP_UNKNOWN                 =  29    # HTTP_CODE_400_BAD_REQUEST
DETAIL_CODE_30_NO_RFID_DATA                         =  30    # HTTP_CODE_500_INTERNAL_SERVER_ERROR
DETAIL_CODE_31_NO_ACTIVE_CHARGE_SESSION             =  31    # HTTP_CODE_400_BAD_REQUEST
DETAIL_CODE_40_PASSWORD_RULE_VIOLATION              =  40    # HTTP_CODE_400_BAD_REQUEST
DETAIL_CODE_41_PASSWORD_TOO_SHORT                   =  41    # HTTP_CODE_400_BAD_REQUEST
DETAIL_CODE_42_PASSWORD_TOO_LONG                    =  42    # HTTP_CODE_400_BAD_REQUEST
DETAIL_CODE_43_PASSWORD_INVALID_CHARACTER           =  43    # HTTP_CODE_400_BAD_REQUEST
DETAIL_CODE_44_PASSWORD_UPPERCASE_REQUIRED          =  44    # HTTP_CODE_400_BAD_REQUEST
DETAIL_CODE_45_PASSWORD_LOWERCASE_REQUIRED          =  45    # HTTP_CODE_400_BAD_REQUEST
DETAIL_CODE_46_PASSWORD_SPECIAL_CHARACTER_REQUIRED  =  46    # HTTP_CODE_400_BAD_REQUEST
DETAIL_CODE_47_TASK_ALREADY_RUNNING                 =  47    # HTTP_CODE_405_METHOD_NOT_ALLOWED
DETAIL_CODE_51_WAKEUP_VEHICLE_FAILED                =  51    # HTTP_CODE_424_FAILED_DEPENDENCY
DETAIL_CODE_200_OK                                  = 200    # HTTP_CODE_200_OK
DETAIL_CODE_202_ACCEPTED                            = 202    # HTTP_CODE_202_ACCEPTED

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

        if (not oppleoConfig.restrictDashboardAccess or
            ( oppleoConfig.allowLocalDashboardAccess and  
                not IPv4.ipInSubnetList(ip=request.remote_addr, subnetList=oppleoConfig.routerIPAddress, default=False) 
            ) or
            current_user.is_authenticated
            ):
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



"""
    Inject {{ now.year }} in each jinja template
    https://stackoverflow.com/questions/41231290/how-to-display-current-year-in-flask-template
"""
@flaskRoutes.context_processor
def inject_now():
    return {'now': datetime.utcnow()}


@flaskRoutes.route('/', methods=['GET'])
@config_dashboard_access_restriction
def index():
    global flaskRoutesLogger, oppleoConfig, changeLog
    flaskRoutesLogger.debug('/ {}'.format(request.method))
    try:
        return render_template(
            'dashboard.html',
            oppleoconfig=oppleoConfig,
            changelog=changeLog
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

def same_origin(current_uri, compare_uri):
    parsed_uri = urlparse(current_uri)
    parsed_compare = urlparse(compare_uri)
    return (parsed_uri.scheme == parsed_compare.scheme and
        parsed_uri.hostname == parsed_compare.hostname and
        parsed_uri.port == parsed_compare.port)

@flaskRoutes.route('/login', methods=['GET'])
def login():
    # For GET requests, display the login form. 
    global flaskRoutesLogger, oppleoConfig
    flaskRoutesLogger.debug('/login {}'.format(request.method))

    if hasattr(current_user, 'authenticated') and current_user.authenticated:
        referrer = request.headers.get("Referer", default=None, type=str)
        # Referrer and on same host?
        if referrer is None or not same_origin(referrer, 'https://{}/'.format(request.host)):
            return redirect('/')
        return redirect(referrer)

    if (request.method == 'GET'):
        return render_template("login.html", 
            oppleoconfig=oppleoConfig,
            changelog=changeLog
            )


@flaskRoutes.route("/<path:username>/login", methods=["POST"])
@flaskRoutes.route("/<path:username>/login/", methods=["POST"])
def login2(username:str=None):
    global flaskRoutesLogger, oppleoConfig, oppleoSystemConfig
    flaskRoutesLogger.debug('/login2 {}'.format(request.method))

    if username is None:
        abort(404)

    # username = request.form.get('user', default=None, type=str)
    password = request.form.get('password', default=None, type=str)
    rememberMe = True if request.form.get('rememberMe', default='false', type=str).lower() in ['true', 't', 1, '1'] else False
    totp = request.form.get('totp', default=None, type=str)

    # Find the user
    user = User.get(username)
    if user is None:
        return jsonify({
            'status'  : HTTP_CODE_401_UNAUTHORIZED,
            'code'    : DETAIL_CODE_26_USERNAME_UNKNOWN,
            'username': username,
            'msg'     : 'Username unknown'
            })                
    # Validate current password
    if not check_password_hash(user.password, password):
        # Password incorrect
        return jsonify({
            'status'  : HTTP_CODE_401_UNAUTHORIZED,
            'code'    : DETAIL_CODE_25_PASSWORD_INCORRECT,
            'username': username,
            'msg'     : 'Password incorrect'
            })                

    # Valid password, 2FA enabled?
    if (user.has_enabled_2FA() and 
            (user.is_2FA_local_enforced() or 
                IPv4.ipInSubnetList(ip=request.remote_addr, subnetList=oppleoConfig.routerIPAddress, default=False)
            )
       ): 
        # Password correct, validate the code
        shared_secret = decryptAES(key=password, encData=user.shared_secret)
        if totp is None or not validateTotp(totp=totp, shared_secret=shared_secret):
            return jsonify({
                'status'  : HTTP_CODE_401_UNAUTHORIZED,
                'code'    : DETAIL_CODE_23_2FA_CODE_INCORRECT,
                'username': username,
                'msg'     : '2FA token required'
                })                
    # Password correct, 2FA correct, log user in
    login_user(user, remember=rememberMe)
    user.authenticated = True
    user.save()

    if oppleoSystemConfig.mqttOutboundEnabled:
        OutboundEvent.emitMQTTEvent( event='login',
                                    data={
                                        "user" : user.username,
                                    },
                                    id=oppleoConfig.chargerName,
                                    namespace='/webclient'
                                    )

    login_next = None
    if 'login_next' in session:
        login_next = session['login_next']
        del session['login_next']

    return jsonify({
        'status'  : HTTP_CODE_200_OK,
        'code'    : DETAIL_CODE_200_OK,
        'username': username,
        '' if login_next is None else 'login_next': login_next,
        'msg'     : 'Loging successful'
        })                
 

@flaskRoutes.route("/logout", methods=["GET"])
@authenticated_resource
#@login_required
def logout():
    global flaskRoutesLogger, oppleoSystemConfig
    flaskRoutesLogger.debug('/logout {}'.format(request.method))
    # Logout the current user
    user = current_user
    user.authenticated = False
    user.save()
    logout_user()
    if oppleoSystemConfig.mqttOutboundEnabled:
        OutboundEvent.emitMQTTEvent( event='logout',
                                    data={
                                        "user" : user.username,
                                    },
                                    id=oppleoConfig.chargerName,
                                    namespace='/webclient'
                                    )

    return redirect(url_for('flaskRoutes.home'))


@flaskRoutes.route("/<path:username>/change_password/", methods=["POST"])
@flaskRoutes.route("/<path:username>/change_password", methods=["POST"])
@authenticated_resource
def change_password(username:str=None):
    global flaskRoutesLogger, oppleoConfig
    flaskRoutesLogger.debug('/change_password {}'.format(request.method))

    if username is None:
        abort(404)

    # username = request.form.get('user', default=None, type=str)
    currentPassword = request.form.get('currentPassword', default=None, type=str)
    newPassword = request.form.get('newPassword', default=None, type=str)
    totp = request.form.get('totp', default=None, type=str)

    """
        TODO: is current user authorized to change password? (later with admin user)
              for now, use current user
    """
    # Validate current password
    if not check_password_hash(current_user.password, currentPassword):
        # Current password incorrect
        return jsonify({
            'status'  : HTTP_CODE_401_UNAUTHORIZED,
            'code'    : DETAIL_CODE_25_PASSWORD_INCORRECT,
            'username': username,
            'msg'     : 'Password incorrect'
            })                
    # Password correct, valid according to rules?
    """
        TODO: configurable password rules
              for now accept any
    """
    # Valid password, 2FA enabled?
    if current_user.has_enabled_2FA():
        # Password correct, validate the code
        shared_secret = decryptAES(key=currentPassword, encData=current_user.shared_secret)
        if totp is None or not validateTotp(totp=totp, shared_secret=shared_secret):
            return jsonify({
                'status'  : HTTP_CODE_401_UNAUTHORIZED,
                'code'    : DETAIL_CODE_23_2FA_CODE_INCORRECT,
                'username': username,
                'msg'     : '2FA token required'
                })                

    # Valid, change the password for the user
    user = current_user
    user.password = generate_password_hash(newPassword)
    # Update the shared secret encryption to the new password
    if current_user.has_enabled_2FA():
        user.shared_secret = encryptAES(key=newPassword, plainData=shared_secret)
    user.save()
    return jsonify({
        'status'  : HTTP_CODE_200_OK,
        'code'    : DETAIL_CODE_200_OK,
        'username': username,
        'msg'     : 'Password updated'
        })                
 

@flaskRoutes.route("/about")
@flaskRoutes.route("/about/")
def about():
    global flaskRoutesLogger, oppleoConfig
    flaskRoutesLogger.debug('/about {}'.format(request.method))
    return render_template("about.html",
                oppleoconfig=oppleoConfig,
                changelog=changeLog
                )

@flaskRoutes.route("/changelog")
@flaskRoutes.route("/changelog/")
def changelog():
    global flaskRoutesLogger, oppleoConfig
    flaskRoutesLogger.debug('/changelog {}'.format(request.method))
    return render_template("changelog.html",
                oppleoconfig=oppleoConfig,
                changelog=changeLog
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
            oppleoconfig=oppleoConfig,
            changelog=changeLog
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
                    oppleoconfig=oppleoConfig,
                    changelog=changeLog
                    )
        flaskRoutesLogger.debug('Shutting down in 2 seconds...')
        # Simple os.system('sudo shutdown now') initiates shutdown before a webpage can be returned
        os.system("nohup sudo -b bash -c 'sleep 2; shutdown now' &>/dev/null")
        return render_template("shuttingdown.html", 
                    oppleoconfig=oppleoConfig,
                    changelog=changeLog
                    )
    else:
        return render_template("authorize.html", 
                form=form, 
                requesttitle="Uitschakelen",
                requestdescription="Schakel het systeem helemaal uit.<br/>Doe dit alleen voor onderhoud aan het systeem. Voor opnieuw opstarten is fysieke toegang tot het systeem vereist!",
                buttontitle="Schakel uit!",
                errormsg="Het wachtwoord is onjuist",
                oppleoconfig=oppleoConfig,
                changelog=changeLog
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
            oppleoconfig=oppleoConfig,
            changelog=changeLog
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
                    oppleoconfig=oppleoConfig,
                    changelog=changeLog
                    )
        flaskRoutesLogger.debug('Rebooting in 2 seconds...')
        # Simple os.system('sudo reboot') initiates reboot before a webpage can be returned
        os.system("nohup sudo -b bash -c 'sleep 2; reboot' &>/dev/null")
        return render_template("rebooting.html", 
                    oppleoconfig=oppleoConfig,
                    changelog=changeLog
                    )
    else:
        return render_template("authorize.html", 
                form=form, 
                requesttitle="Reboot",
                requestdescription="Reboot het systeem.<br/>Doe dit alleen als het systeem zich inconsistent gedraagd. <br />Dit zal ongeveer 40 seconden duren.",
                buttontitle="Reboot!",
                errormsg="Het wachtwoord is onjuist",
                oppleoconfig=oppleoConfig,
                changelog=changeLog
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
            oppleoconfig=oppleoConfig,
            changelog=changeLog
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
                    oppleoconfig=oppleoConfig,
                    changelog=changeLog
                    )

        flaskRoutesLogger.debug('Restart requested and authorized. Restarting in 2 seconds...')
        # Simple os.system('sudo systemctl restart Oppleo.service') initiates restart before a webpage can be returned
        try:
            os.system("nohup sudo -b bash -c 'sleep 2; systemctl restart Oppleo.service' &>/dev/null")
        except Exception as e:
            pass
        return render_template("restarting.html", 
                    oppleoconfig=oppleoConfig,
                    changelog=changeLog
                    )
    else:
        return render_template("authorize.html", 
                form=form, 
                requesttitle="Herstarten",
                requestdescription="Herstart de applicatie.<br/>Doe dit alleen als een nieuwe configuratie geladen moet worden. Het herstarten van de applicatie duurt ongeveer 10 seconden.",
                buttontitle="Herstart!",
                errormsg="Het wachtwoord is onjuist",
                oppleoconfig=oppleoConfig,
                changelog=changeLog
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
            requestdescription="Update de applicatie.<br/>Doe dit alleen als een nieuwe configuratie geladen moet worden. Het updaten van de applicatie kan tot 1 minuut duren.",
            requestdescriptionclass="text-center text-warning",
            buttontitle="Update!",
            oppleoconfig=oppleoConfig,
            changelog=changeLog
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
                    requestdescription="Update de applicatie.<br/>Doe dit alleen als een nieuwe configuratie geladen moet worden. Het updaten van de applicatie kan tot 1 minuut duren.",
                    buttontitle="Herstart!",
                    errormsg="Er wordt momenteel een backup gemaakt. Probeer het later normaals.",
                    oppleoconfig=oppleoConfig,
                    changelog=changeLog
                    )

        flaskRoutesLogger.debug('Updating in 2 seconds...')
        try: 
            updateSoftwareInstallCmd = os.path.join(os.path.dirname(os.path.realpath(__file__)).split('src/nl/oppleo/webapp')[0], 'install/install.sh')
            updateSoftwareLogFile = os.path.join(os.path.dirname(os.path.realpath(__file__)).split('src/nl/oppleo/webapp')[0], 'install/log/update_{}.log'.format(datetime.now().strftime("%Y%m%d%H%M%S")))
            # os.system("nohup sudo -b bash -c 'sleep 2; /home/pi/Oppleo/install/install.sh service' &>/dev/null")
            # online is the keyword for install.sh for not killing the Oppleo.service!
            # 20210525 skipping online keyword, KillMode=process should only kill the Oppleo process, not this install script
            # flaskRoutesLogger.debug("nohup sudo -u pi -b bash -c 'sleep 2; {} online &> {}'".format(updateSoftwareInstallCmd, updateSoftwareLogFile))
            # os.popen("nohup sudo -u pi -b bash -c 'sleep 2; {} online &> {}'".format(updateSoftwareInstallCmd, updateSoftwareLogFile))
            flaskRoutesLogger.debug("nohup sudo -u pi -b bash -c 'sleep 2; {} &> {}'".format(updateSoftwareInstallCmd, updateSoftwareLogFile))
            os.popen("nohup sudo -u pi -b bash -c 'sleep 2; {} &> {}'".format(updateSoftwareInstallCmd, updateSoftwareLogFile))
            # update script kills Oppleo, and also os.system or os.popen processes. Spawn new process that will survive the Oppleo kill
            oppleoConfig.softwareUpdateInProgress = True
        except Exception as e:
            flaskRoutesLogger.error("Exception running software update! {}".format(e))
        return render_template("softwareupdate.html", 
                    oppleoconfig=oppleoConfig,
                    changelog=changeLog
                    )
    else:
        return render_template("authorize.html", 
                form=form, 
                requesttitle="Software Update",
                requestdescription="Update de applicatie.<br/>Doe dit alleen als een nieuwe configuratie geladen moet worden. Het updaten van de applicatie kan 30 seconden tot 1 minuut duren.",
                buttontitle="Herstart!",
                errormsg="Het wachtwoord is onjuist",
                oppleoconfig=oppleoConfig,
                changelog=changeLog
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
            oppleoconfig=oppleoConfig,
            changelog=changeLog
            )
    # For POST requests, login the current user by processing the form.
    form = AuthorizeForm()
    if form.validate_on_submit() and \
       check_password_hash(current_user.password, form.password.data):
        flaskRoutesLogger.debug('delete_charge_session requested and authorized.')
        charge_session = ChargeSessionModel.get_one_charge_session(id)
        charge_session.delete()
        flaskRoutesLogger.debug('delete_charge_session() - id:{} - deleted'.format(id))
        # Send ws update
        OutboundEvent.triggerEvent(
                event='charge_session_deleted',
                id=oppleoConfig.chargerName,
                data={ 'deleteId': id },
                namespace='/charge_session',
                public=False
            )
        return redirect(url_for('flaskRoutes.charge_sessions'))
    else:
        return render_template("authorize.html", 
                form=form, 
                requesttitle=str("Laadsessie " + str(id)),
                buttontitle=str("Verwijder laadsessie " + str(id)),
                errormsg="Het wachtwoord is onjuist",
                oppleoconfig=oppleoConfig,
                changelog=changeLog
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
            oppleoconfig=oppleoConfig,
            changelog=changeLog
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
                        oppleoconfig=oppleoConfig,
                        changelog=changeLog
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
                oppleoconfig=oppleoConfig,
                changelog=changeLog
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
            oppleoconfig=oppleoConfig,
            changelog=changeLog
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
                oppleoconfig=oppleoConfig,
                changelog=changeLog
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
                oppleoconfig=oppleoConfig,
                changelog=changeLog
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
                oppleoconfig=oppleoConfig,
                changelog=changeLog
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
                oppleoconfig=oppleoConfig,
                changelog=changeLog
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
    diag['threading']['rfid_log'] = oppleoConfig.chThread.rfidReaderLog()
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
    edmm = EnergyDeviceMeasureModel()
    edmm.energy_device_id = oppleoConfig.energyDevice
    diag['measurements'] = edmm.get_count()
    diag['measurements_str'] = '{:,}'.format(edmm.get_count()).replace(',', '.')

    charger_config_str = ChargerConfigModel().get_config().to_str()
    return render_template("settings.html", 
                active=active, 
                diag=diag, 
                diag_json=diag_json,
                charger_config=charger_config_str,
                energydevicemodel=EnergyDeviceModel.get(),
                oppleosystemconfig=oppleoSystemConfig,
                oppleoconfig=oppleoConfig,
                backuputil=BackupUtil(),
                changelog=changeLog,
                gitutil=GitUtil,
                ipv4=IPv4
            )


"""
    Get Usage data timestamp entry
"""
@flaskRoutes.route("/usage_data_tse/<path:ts>", methods=["GET"])
@flaskRoutes.route("/usage_data_tse/<path:ts>/", methods=["GET"])
@config_dashboard_access_restriction
def usage_data_tse(ts:str=None):
    global flaskRoutesLogger
    flaskRoutesLogger.debug('/usage_data_tse/')

    device_measurement = EnergyDeviceMeasureModel()
    device_measurement.energy_device_id = oppleoConfig.chargerName

    recordsTotal = device_measurement.get_count()

    entry_id = device_measurement.get_count_at_timestamp(energy_device_id=oppleoConfig.chargerName, 
                                                            ts=device_measurement.date_str_to_datetime(ts)
                                                        )
    return {
            "recordsTotal": recordsTotal,
            "timestamp": ts,
            "entry": entry_id
        }
                          


"""
    TODO: search
           - zoek in alle searchable velden
           - zoek op specifieke datum/tijd
"""

@flaskRoutes.route("/usage_data_ssdt", methods=["GET"])
@flaskRoutes.route("/usage_data_ssdt/", methods=["GET"])
@config_dashboard_access_restriction
def usage_data_serviceside_datatable():
    global flaskRoutesLogger
    flaskRoutesLogger.debug('/usage_data_ssdt/')

    """ Default column order """
    defaultColumns = [ 'created_at', 'kw_total', 'kwh_l1', 'kwh_l2', 'kwh_l3', 'a_l1', 'a_l2', 'a_l3', 
                       'p_l1', 'p_l2', 'p_l3', 'v_l1', 'v_l2', 'v_l3', 'hz' ]

    method = request.method
    draw = request.args.get('draw', default=0, type=int)
    start = request.args.get('start', default=0, type=int)
    length = request.args.get('length', default=0, type=int)
    searchValue = request.args.get('search[value]', default='', type=str)
    searchRegex = request.args.get('search[regex]', default=False, type=bool)
    orderColumn = request.args.get('order[0][column]', default=0, type=int)
    orderDir = request.args.get('order[0][dir]', default='asc', type=str)

    columnList = []
    i = 0
    while request.args.get(f'columns[{i}][data]', default=None, type=str) is not None:
        columnList.append({ 'name'          : request.args.get(f'columns[{i}][name]', default=defaultColumns[i] if i in defaultColumns else '', type=str), 
                            'data'          : request.args.get(f'columns[{i}][data]', default=defaultColumns[i] if i in defaultColumns else '', type=str), 
                            'searchable'    : True if request.args.get(f'columns[{i}][searchable]', default='false', type=str) in ['true'] else False,
                            'orderable'     : True if request.args.get(f'columns[{i}][orderable]', default='false', type=str) in ['true'] else False,
                            'searchValue'   : request.args.get(f'columns[{i}][search][value]', default='', type=str), 
                            'searchRegex'   : True if request.args.get(f'columns[{i}]search][regex]', default='false', type=str) in ['true'] else False
                          })
        i += 1
    if len(columnList) == 0:
        """ Default """
        for column in defaultColumns:
            columnList.append({ 'name'          : column, 
                                'data'          : column, 
                                'searchable'    : True,
                                'orderable'     : True,
                                'searchValue'   : '', 
                                'searchRegex'   : False
                            })

    device_measurement = EnergyDeviceMeasureModel()
    device_measurement.energy_device_id = oppleoConfig.chargerName

    recordsTotal = device_measurement.get_count()

    """ 
        Filter or search 
        - create_at is search from (if order asc) or untill (if order is desc)
        - other column search not yet supported
    """
    created_at = next((column for column in columnList if column['data'] == 'created_at'), None)

    if 'searchValue' in created_at and created_at['searchValue'] != '':
        """ search for date """
        entry_id = device_measurement.get_count_at_timestamp(energy_device_id=oppleoConfig.chargerName, 
                                                             ts=device_measurement.date_str_to_datetime(created_at['searchValue'])
                                                            )
        """ Default order desc, start at the entry (or -1?) """
        start = entry_id
        """ If order asc, start at total - entry - length """
        if orderColumn == columnList.index(created_at) and orderDir.lower() == 'asc':
            start = recordsTotal - entry_id - length


    qr = device_measurement.paginate(energy_device_id = oppleoConfig.chargerName,
                                     offset           = start, 
                                     limit            = length, 
                                     orderColumn      = getattr(EnergyDeviceMeasureModel, columnList[orderColumn]['data']),
                                     orderDir         = orderDir
                                    )
    qr_pl = []
    for o in qr:
        entry = {}
        for column in columnList:
            if column['data'] == 'created_at':
                entry['created_at'] = o.get_created_at_str()
            else:
                entry[column['data']] = getattr(o, column['data'])
        qr_pl.append(entry)

    return {
            "draw": draw,
            "recordsTotal": recordsTotal,
            "recordsFiltered": recordsTotal,
            "start": start,
            "length": length,
            "data": qr_pl
        }


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


@flaskRoutes.route("/charge_session/<path:id>/usage_data", methods=["GET"])
@flaskRoutes.route("/charge_session/<path:id>/usage_data/", methods=["GET"])
@config_dashboard_access_restriction
def charge_session_usage_data(id=None):
    global flaskRoutesLogger

    flaskRoutesLogger.debug('/charge_session/{}/usage_data/'.format(id))
    
    chargeSession = ChargeSessionModel.get_one_charge_session(id=id)
    if (chargeSession is None):
        return jsonify({ 
            'status'        : HTTP_CODE_404_NOT_FOUND,
            'id'            : id
            })

    device_measurement = EnergyDeviceMeasureModel()
    device_measurement.energy_device_id = oppleoConfig.chargerName

    qr = device_measurement.get_between(energy_device_id=oppleoConfig.chargerName, 
                                        since_ts=chargeSession.start_time, 
                                        until_ts=chargeSession.end_time if chargeSession.end_time is not None else datetime.now()
                                        )
    qr_l = []
    for o in qr:
        qr_l.append(o.to_dict())  

    return jsonify({ 
            'status'        : HTTP_CODE_200_OK,
            'id'            : id,
            'data'          : qr_l
            })



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
                    oppleoconfig=oppleoConfig,
                    changelog=changeLog
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


@flaskRoutes.route("/charge_session/<path:id>/update", methods=["POST"])
@flaskRoutes.route("/charge_session/<path:id>/update/", methods=["POST"])
@authenticated_resource
def charge_session(id:int=None):
    global flaskRoutesLogger, oppleoConfig

    id = request.form.get('session', default='None', type=str)

    # First validate password
    password = request.form.get('password', default='None', type=str)
    if password is None or not check_password_hash(current_user.password, password):
        return jsonify({ 'status': HTTP_CODE_401_UNAUTHORIZED, 'session': -1 if id is None else id, 'reason' : 'Authorization error' })

    try:
        jsonD = json.loads(request.form.get('data', default='None', type=str))
    except JSONDecodeError as jde:
        return jsonify({ 'status': HTTP_CODE_400_BAD_REQUEST, 'session': -1 if id is None else id, 'reason' : 'JSON decode error' })

    fieldValidation = { 'start_value'       : "^[0-9]*[,|.]?[0-9]?$",
                        'km'                : "^[0-9]*$",
                        'end_value'         : "^[0-9]*[,|.]?[0-9]?$",
                        'energy_device_id'  : "^[0-9]|[a-z]|[A-Z]|[!@#$%\^&*._\-]+$",
                        'tariff'            : "^(?:0|[1-9][0-9]*)(?:[.][0-9]{1,2})?$" 
                      }

    """ 
        NOTE: don't use 
            chargeSession.__dict__[fieldName] = X 
        sqlalchemy doesn't detect the change and will not save it on commit. Use 
            setattr(obj, field, value)
        instead.
    """


    chargeSession = ChargeSessionModel.get_one_charge_session(id)
    resultDict = {}
    for fieldName in chargeSession.fieldList:
        resultDict[fieldName] = { 'updated': False }
        if ( (fieldName in jsonD) and
            ( ( fieldName in ['start_time', 'end_time'] and 
                ( getattr(chargeSession, fieldName) == None or chargeSession.datetime_to_date_str( getattr(chargeSession, fieldName) ) != jsonD[fieldName] )
              ) or
              ( fieldName in ['start_value', 'end_value', 'tariff'] and 
                getattr(chargeSession, fieldName) != jsonD[fieldName] and 
                jsonD[fieldName] != '' and 
                isinstance(jsonD[fieldName], (str, int, float)) and 
                ( getattr(chargeSession, fieldName) == None or float(getattr(chargeSession, fieldName)) != float(jsonD[fieldName]) )
              ) or
              ( fieldName in ['km'] and 
                getattr(chargeSession, fieldName) != jsonD[fieldName] and 
                isinstance(jsonD[fieldName], (str, int)) and 
                ( getattr(chargeSession, fieldName) == None or jsonD[fieldName] == '' or int(getattr(chargeSession, fieldName)) != int(jsonD[fieldName]) )
              ) or
              ( fieldName not in ['start_time', 'end_time', 'start_value', 'end_value', 'tariff', 'km'] and 
                getattr(chargeSession, fieldName) != jsonD[fieldName] and 
                ( getattr(chargeSession, fieldName) == None or str(getattr(chargeSession, fieldName)) != jsonD[fieldName] )
              )
            )
           ):
            if fieldName in ['start_time', 'end_time']:
                # datetime
                try:
                    setattr(chargeSession, fieldName, chargeSession.date_str_to_datetime(jsonD[fieldName]))
                except ValueError as ve:
                    return jsonify({ 'status': HTTP_CODE_400_BAD_REQUEST, 'session': -1 if id is None else id, 'reason' : 'Field format error ({})'.format(fieldName) })
            elif fieldName in ['start_value', 'end_value', 'tariff']:
                if fieldName in fieldValidation and not re.match(fieldValidation[fieldName], jsonD[fieldName]):
                    # Not valid
                    return jsonify({ 'status': HTTP_CODE_400_BAD_REQUEST, 'session': -1 if id is None else id, 'reason' : 'Field format error ({})'.format(fieldName) })
                # float
                try:
                    setattr(chargeSession, fieldName, float(jsonD[fieldName]) if jsonD[fieldName] != '' else None)
                except ValueError as ve:
                    return jsonify({ 'status': HTTP_CODE_400_BAD_REQUEST, 'session': -1 if id is None else id, 'reason' : 'Field type error ({})'.format(fieldName) })
            elif fieldName in ['km']:
                if fieldName in fieldValidation and not re.match(fieldValidation[fieldName], jsonD[fieldName]):
                    # Not valid
                    return jsonify({ 'status': HTTP_CODE_400_BAD_REQUEST, 'session': -1 if id is None else id, 'reason' : 'Field format error ({})'.format(fieldName) })
                # float
                try:
                    setattr(chargeSession, fieldName, int(jsonD[fieldName]) if jsonD[fieldName] != '' else None)
                except ValueError as ve:
                    return jsonify({ 'status': HTTP_CODE_400_BAD_REQUEST, 'session': -1 if id is None else id, 'reason' : 'Field type error ({})'.format(fieldName) })
            elif fieldName in ['trigger']:
                if ( jsonD[fieldName].upper() in [ChargeSessionModel.TRIGGER_RFID, ChargeSessionModel.TRIGGER_AUTO, ChargeSessionModel.TRIGGER_WEB] and
                     jsonD[fieldName].upper() != getattr(chargeSession, fieldName) ):
                    setattr(chargeSession, fieldName, jsonD[fieldName])
                else:
                    return jsonify({ 'status': HTTP_CODE_400_BAD_REQUEST, 'session': -1 if id is None else id, 'reason' : 'Field value error ({})'.format(fieldName) })
            else:
                if fieldName in fieldValidation and not re.match(fieldValidation[fieldName], jsonD[fieldName]):
                    # Not valid
                    return jsonify({ 'status': HTTP_CODE_400_BAD_REQUEST, 'session': -1 if id is None else id, 'reason' : 'Field format error ({})'.format(fieldName) })
                # str
                setattr(chargeSession, fieldName, jsonD[fieldName])
            resultDict[fieldName] = { 'updated': True, 'value': jsonD[fieldName] }

    # Calulate total energy and total price
    total_energy = float(chargeSession.end_value) - float(chargeSession.start_value)
    if total_energy != chargeSession.total_energy:
        chargeSession.total_energy = total_energy
        resultDict['total_energy'] = { 'updated': True, 'value': total_energy }

    total_price = round(chargeSession.total_energy * chargeSession.tariff * 100) /100
    if total_price != chargeSession.total_price:
        chargeSession.total_price = total_price
        resultDict['total_price'] = { 'updated': True, 'value': total_price }

    # Store the changes
    chargeSession.save()

    OutboundEvent.triggerEvent(
            event='charge_session_data_update', 
            id=oppleoConfig.chargerName,
            data=chargeSession.to_str(), 
            namespace='/charge_session',
            public=False
        )

    return jsonify({ 
            'status'    : HTTP_CODE_200_OK,
            'session'   : id,
            'update'    : resultDict
        })



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
                oppleoconfig=oppleoConfig,
                changelog=changeLog
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
                oppleoconfig=oppleoConfig,
                changelog=changeLog
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
                oppleoconfig=oppleoConfig,
                changelog=changeLog
                )
        rfid_model = RfidModel().get_one(token)
        if (rfid_model == None):
            return render_template(
                'tokens.html', 
                oppleoconfig=oppleoConfig,
                changelog=changeLog
            )

        # TODO Add vehicle api token information

        rfid_change_form = RfidChangeForm()
        flaskRoutesLogger.debug('CSRF Token: {}'.format(rfid_change_form.csrf_token.current_token) )
        if (request.method == 'DELETE'):
            # Not allowed
            abort(405)

        if (request.method == 'POST'):
            # Not allowed
            abort(405)
 

        vehicle_list = []
        vApi = VehicleApi(rfid_model=rfid_model)
        account_linked=vApi.isAuthorized()
        if vApi.isAuthorized():
            vehicle_list=vApi.getVehicleList()
            for vehicle in vehicle_list:
                vFilename = rfid_model.getVehicleFilename()
                vFilePath = os.path.join(app.config['VEHICLE_FOLDER'], vFilename)
                if os.path.exists(vFilePath):
                    vehicle['vehicle_img'] = vFilename
        return render_template("token.html",
                    rfid_model=rfid_model,
                    account_linked=account_linked,
                    vehicle_list=map(json.dumps, vehicle_list),
                    form=rfid_change_form,
                    oppleoconfig=oppleoConfig,
                    changelog=changeLog
                )


    if (token is None and request.method != 'GET'):
        return jsonify({ 'status': HTTP_CODE_400_BAD_REQUEST, 'reason' : 'No token id (RFID)' })

    rfid_model = None
    if (token is not None):
        # Specific token
        rfid_model = RfidModel().get_one(token)
        if (rfid_model is None):
            return jsonify({ 'status': HTTP_CODE_404_NOT_FOUND, 'reason' : 'Token id (RFID) not found' })

    # JSON 
    if (request.method == 'GET'):
        # Check if token exist, if not rfid is None
        if (rfid_model is None):
            rfid_list = []
            rfid_models = RfidModel().get_all()
            for rfid_model in rfid_models:

                # TODO Clean expired vehicle api tokens

                entry = rfid_model.to_str()
                # Add wether token has charge sessions
                entry['chargeSessions'] = ChargeSessionModel.get_charge_session_count_for_rfid(rfid_model.rfid)
                entry['get_odometer'] = True if rfid_model.get_odometer else False
                vApi = VehicleApi(rfid_model=rfid_model)
                entry['make_api_authorized'] = vApi.isAuthorized()

                vFilename = rfid_model.getVehicleFilename()
                vFilePath = os.path.join(app.config['VEHICLE_FOLDER'], vFilename)
                if os.path.exists(vFilePath):
                    entry['vehicle_img'] = vFilename

                rfid_list.append(entry)
            return jsonify(rfid_list)
        # Specific token

        # TODO Clean expired vehicle api tokens

        entry = rfid_model.to_str()
        # Add wether token has charge sessions
        entry['chargeSessions'] = ChargeSessionModel.get_charge_session_count_for_rfid(rfid_model.rfid)
        vApi = VehicleApi(rfid_model=rfid_model)
        entry['make_api_authorized'] = vApi.isAuthorized()

        vFilename = rfid_model.getVehicleFilename()
        vFilePath = os.path.join(app.config['VEHICLE_FOLDER'], vFilename)
        if os.path.exists(vFilePath):
            entry['vehicle_img'] = vFilename

        return jsonify(entry)


    # JSON 
    if (request.method == 'DELETE'):
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


    if (request.method == 'POST'):
        # Update for specific token

        result = { 'rfid' : token }
        # rfid - in url
        if request.json['rfid'] is None or not isinstance(request.json['rfid'], str) or request.json['rfid'] != token:
            return jsonify({ 'status': HTTP_CODE_400_BAD_REQUEST, 'reason' : 'Token id (RFID) does not match' })

        if 'name' in request.json and request.json['name'] is not None and isinstance(request.json['name'], str):
            rfid_model.name = request.json['name']
            result['name'] = rfid_model.name

        if 'enabled' in request.json and request.json['enabled'] is not None and isinstance(request.json['enabled'], bool):
            rfid_model.enabled = request.json['enabled']
            result['enabled'] = rfid_model.enabled

        if 'valid_from' in request.json and request.json['valid_from'] is not None and isinstance(request.json['valid_from'], str):
            try:
                if len(request.json['valid_from']) > 0:
                    rfid_model.valid_from = datetime.strptime(request.json['valid_from'], '%d %B %Y')
                    result['valid_from'] = rfid_model.valid_from.strftime('%d %B %Y')
                else:
                    rfid_model.valid_from = None
                    result['valid_from'] = None
            except Exception as e:
                pass
        if 'valid_until' in request.json and request.json['valid_until'] is not None and isinstance(request.json['valid_until'], str):
            try:
                if len(request.json['valid_until']) > 0:
                    rfid_model.valid_until = datetime.strptime(request.json['valid_until'], '%d %B %Y')
                    result['valid_until'] = rfid_model.valid_until.strftime('%d %B %Y')
                else:
                    rfid_model.valid_until = None
                    result['valid_until'] = None
            except Exception as e:
                pass

        if 'vehicle_make' in request.json and request.json['vehicle_make'] is not None and isinstance(request.json['vehicle_make'], str):
            rfid_model.vehicle_make = request.json['vehicle_make']
            result['vehicle_make'] = rfid_model.vehicle_make

        if 'vehicle_model' in request.json and request.json['vehicle_model'] is not None and isinstance(request.json['vehicle_model'], str):
            rfid_model.vehicle_model = request.json['vehicle_model']
            result['vehicle_model'] = rfid_model.vehicle_model
        if 'license_plate' in request.json and request.json['license_plate'] is not None and isinstance(request.json['license_plate'], str):
            rfid_model.license_plate = request.json['license_plate']
            result['license_plate'] = rfid_model.license_plate
        if 'vehicle_vin' in request.json and request.json['vehicle_vin'] is not None and isinstance(request.json['vehicle_vin'], str):
            rfid_model.vehicle_vin = request.json['vehicle_vin']
            result['vehicle_vin'] = rfid_model.vehicle_vin
        if 'vehicle_name' in request.json and request.json['vehicle_name'] is not None and isinstance(request.json['vehicle_name'], str):
            rfid_model.vehicle_name = request.json['vehicle_name']
            result['vehicle_name'] = rfid_model.vehicle_name

        if 'get_odometer' in request.json and request.json['get_odometer'] is not None and isinstance(request.json['get_odometer'], bool):
            rfid_model.get_odometer = request.json['get_odometer']
            result['get_odometer'] = rfid_model.get_odometer

        rfid_model.save()

        return jsonify({
            'status' : HTTP_CODE_200_OK, 
            'result' : result
            })

    # Not allowed
    abort(405)


"""
    Currently this method is not working.
    Tesla is only implemented vehicle api, and it doesnot support OAuth2 token generation from username/password
    without head (browser)
    TODO: debug when working
"""
# Always returns json
@flaskRoutes.route("/rfid_tokens/<path:token>/VehicleApi/GenerateOAuth", methods=["POST"])
@flaskRoutes.route("/rfid_tokens/<path:token>/VehicleApi/GenerateOAuth/", methods=["POST"])
@authenticated_resource  # CSRF Token is valid
def VehicleApi_GenerateOAuth(token=None):
    global flaskRoutesLogger
    flaskRoutesLogger.debug('/rfid_tokens/{}/VehicleApi/GenerateOAuth {}'.format(token, request.method))
    flaskRoutesLogger.debug('/rfid_tokens/{}/VehicleApi/GenerateOAuth method: {} token: {}'.format(token, request.method, token))
    rfid_model = RfidModel().get_one(token)
    if ((token == None) or (rfid_model == None)):
        # Nope, no token
        return jsonify({
            'status': HTTP_CODE_404_NOT_FOUND, 
            'reason': 'No known RFID token'
            })

    """
        TODO
        ! This is not working at the time
    """

    # Update for specific token
    vApi = VehicleApi()
    rfid_model.api_account=request.form['oauth_email']
    vApi.authorizeByUsernamePassword(rfid_model=rfid_model, user=request.form['oauth_email'], password=request.form['oauth_password'])

    if vApi.isAuthorized():
        # Obtained token
        rfid_model.save()
        return jsonify({
            'status': HTTP_CODE_200_OK, 
            'vehicles' : vApi.getVehicleList()
            })
    else:
        # Nope, no token
        rfid_model.api_account=None
        rfid_model.vehicle_name=None
        return jsonify({
            'status': HTTP_CODE_401_UNAUTHORIZED,  
            'reason': 'Not authorized'
            })

"""
    TODO
    Current implementation has Tesla make only
    Current tesla api does not support refreshing token
"""
# Always returns json
@flaskRoutes.route("/rfid_tokens/<path:token>/VehicleApi/RefreshOAuth", methods=["POST"])
@flaskRoutes.route("/rfid_tokens/<path:token>/VehicleApi/RefreshOAuth/", methods=["POST"])
@authenticated_resource
def VehicleApi_RefreshOAuth(token=None):
    global flaskRoutesLogger
    flaskRoutesLogger.debug('/rfid_tokens/{}/VehicleApi/RefreshOAuth {}'.format(token, request.method))
    flaskRoutesLogger.debug('/rfid_tokens/{}/VehicleApi/RefreshOAuth method: {} token: {}'.format(token, request.method, token))

    return jsonify({
        'status': HTTP_CODE_404_NOT_FOUND, 
        'reason': 'Not supported'
        })


    rfid_model = RfidModel().get_one(token)
    if ((token == None) or (rfid_model == None)):
        # Nope, no token
        return jsonify({
            'status': HTTP_CODE_404_NOT_FOUND, 
            'reason': 'No known RFID token'
            })
    # Update for specific token
    vApi = VehicleApi()
    if not vApi.refreshToken():
        return jsonify({
            'status': HTTP_CODE_500_INTERNAL_SERVER_ERROR,
            'reason': 'Refresh failed'
            })
    # Refresh succeeded, Obtained token
    UpdateOdometerTeslaUtil.copy_token_from_api_to_rfid_model(tesla_api, rfid_model)
    rfid_model.save()

    return jsonify({
        'status': HTTP_CODE_200_OK, 
        'vehicles' : vApi.getVehicleList()
        })


"""
    Specific TeslaPy implementation to generate the login URL
"""
# Always returns json
@flaskRoutes.route("/VehicleApi/AuthURL", methods=["GET"])
@flaskRoutes.route("/VehicleApi/AuthURL/", methods=["GET"])
@authenticated_resource
def VehicleApi_OAuthURL(token=None):
    global flaskRoutesLogger
    flaskRoutesLogger.debug('/rfid_tokens/{}/VehicleApi/OAuthURL {}'.format(token, request.method))
    flaskRoutesLogger.debug('/rfid_tokens/{}/VehicleApi/OAuthURL method: {} token: {}'.format(token, request.method, token))

    account = request.args.get('account', default=None, type=str)
    vehicle_make = request.args.get('vehicle_make', default=None, type=str)
    logout = request.args.get('logout', default=None, type=str)
    if account is None:
        return jsonify({
            'status': HTTP_CODE_500_INTERNAL_SERVER_ERROR,
            'reason': 'Missing account parameter'
            })

    vApi = VehicleApi(account)
    return jsonify({
        'status': HTTP_CODE_200_OK, 
        'direction' : 'login' if logout is None else 'logout',
        'url': vApi.getAuthorizationUrl(account=account, vehicle_make=vehicle_make) if logout is None else vApi.logout(account=account, vehicle_make=vehicle_make)
        })


"""
    {
        "vehicle_make"  : "Tesla",             # make identifying the api
        "account"       : "me@world.com",      # email address connected to the vehicle manufacturer account
        "token"         : "123"                 # The refresh token, or the URL after the browser login (Tesla)
    }
"""
# Always returns json
@flaskRoutes.route("/rfid_tokens/<path:token>/VehicleApi/ValidateTokenOrUrl", methods=["POST"])
@flaskRoutes.route("/rfid_tokens/<path:token>/VehicleApi/ValidateTokenOrUrl/", methods=["POST"])
@authenticated_resource  # CSRF Token is valid
def ValidateTokenOrUrl(token=None):
    global flaskRoutesLogger
    flaskRoutesLogger.debug('/rfid_tokens/{}/VehicleApi/ValidateTokenOrUrl {}'.format(token, request.method))
    flaskRoutesLogger.debug('/rfid_tokens/{}/VehicleApi/ValidateTokenOrUrl method: {} token: {}'.format(token, request.method, token))

    jsonRequested = ('CONTENT_TYPE' in request.environ and 
                     request.environ['CONTENT_TYPE'].lower() == 'application/json')

    rfid_model = RfidModel().get_one(token)
    if ((token == None) or (rfid_model == None)):
        # Nope, no token
        return jsonify({
            'status': HTTP_CODE_404_NOT_FOUND, 
            'reason': 'No known RFID token'
            })

    if request.json['account'] is None or request.json['token'] is None:
        return jsonify({ 'status': HTTP_CODE_400_BAD_REQUEST, 'session': -1 if id is None else id, 'reason' : 'Missing parameter (account or token)' })

    # Update for specific token
    vApi = VehicleApi(rfid_model=rfid_model)
    authorized = False
    if validators.url(request.json['token']):
        # URL
        authorized = vApi.authorizeByUrl(vehicle_make=request.json['vehicle_make'], account=request.json['account'], url=request.json['token'])
    else:
        # refresh token
        authorized = vApi.authorizeByRefreshToken(vehicle_make=request.json['vehicle_make'], account=request.json['account'], refresh_token=request.json['token'])
    if authorized:
        # Obtained token
        rfid_model.api_account=request.json['account']
        rfid_model.save()

        """
            Create a vehicle img if available
        """
        vehicleList = vApi.getVehicleList()
        for vehicle in vehicleList:
            vImg = vApi.composeImage(vin=vehicle['vin'])
            if vImg is not None:
                # Determine unique and non-existing filename

                vFilename = rfid_model.getVehicleFilename()
                vFilePath = os.path.join(app.config['VEHICLE_FOLDER'], vFilename)
                # Save the vehicle img to it. Open file in binary write mode
                vFile = open(vFilePath, "wb")
                # Write bytes to file
                vFile.write(vImg)
                # Close file
                vFile.close()
                vehicle['vehicle_img'] = vFilename

        return jsonify({
            'status': HTTP_CODE_200_OK, 
            'vehicles' : vehicleList
            })
    else:
        # Nope, no token
        rfid_model.api_account=None
        return jsonify({
            'status': HTTP_CODE_401_UNAUTHORIZED,  
            'reason': 'Not authorized'
            })



# Always returns json
@flaskRoutes.route("/rfid_tokens/<path:token>/VehicleApi/Unlink", methods=["POST"])
@flaskRoutes.route("/rfid_tokens/<path:token>/VehicleApi/Unlink/", methods=["POST"])
@authenticated_resource  # CSRF Token is valid
def UnlinkVehicleApi(token=None):
    global flaskRoutesLogger
    flaskRoutesLogger.debug('/rfid_tokens/{}/VehicleApi/Unlink {}'.format(token, request.method))
    rfid_model = RfidModel().get_one(token)
    if ((token == None) or (rfid_model == None)):
        # Nope, no token
        return jsonify({
            'status': HTTP_CODE_404_NOT_FOUND, 
            'reason': 'No known RFID token'
            })

    # Update for specific token
    vApi = VehicleApi(rfid_model=rfid_model)
    vApi.logout()

    vFilename = rfid_model.getVehicleFilename()
    vFilePath = os.path.join(app.config['VEHICLE_FOLDER'], vFilename)
    if os.path.exists(vFilePath):
        os.remove(vFilePath)

    vehicle_make = rfid_model.vehicle_make
    account = rfid_model.api_account
    rfid_model.cleanupVehicleInfo()

    return jsonify({
            'status'        : HTTP_CODE_200_OK, 
            'action'        : 'unlinkVehicleApi',
            'vehicle_make'  : vehicle_make,
            'account'       : account
            })


# Always returns json
@flaskRoutes.route("/rfid_tokens/<path:token>/VehicleApi/RevokeOAuth", methods=["POST"])
@flaskRoutes.route("/rfid_tokens/<path:token>/VehicleApi/RevokeOAuth/", methods=["POST"])
@authenticated_resource
def VehicleApi_RevokeOAuth(token=None):
    global flaskRoutesLogger
    flaskRoutesLogger.debug('/rfid_tokens/{}/VehicleApi/RevokeOAuth {}'.format(token, request.method))
    flaskRoutesLogger.debug('/rfid_tokens/{}/VehicleApi/RevokeOAuth method: {} token: {}'.format(token, request.method, token))
    rfid_model = RfidModel().get_one(token)
    if ((token == None) or (rfid_model == None)):
        # Nope, no token
        return jsonify({
            'status': HTTP_CODE_404_NOT_FOUND, 
            'reason': 'No known RFID token'
            })
    # Update for specific token
    vApi = VehicleApi(rfid_model=rfid_model)
    vApi.logout()

    vFilename = rfid_model.getVehicleFilename()
    vFilePath = os.path.join(app.config['VEHICLE_FOLDER'], vFilename)
    if os.path.exists(vFilePath):
        os.remove(vFilePath)

    rfid_model.api_account = None
    rfid_model.get_odometer = None
    rfid_model.vehicle_name = None
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


    if (param == 'offpeakEnabled'):
        oppleoConfig.offpeakEnabled = True if value.lower() in ['true', '1', 't', 'y', 'yes'] else False
        ophm = OffPeakHoursModel()
        OutboundEvent.triggerEvent(
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
        OutboundEvent.triggerEvent(
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
    # With an open charge session, there params are not allowed to change
    if (param == 'chargerName' and
        ChargeSessionModel.has_open_charge_session_for_device(oppleoConfig.chargerName)):
        return jsonify({ 'status': 409, 'param': param, 'reason': 'Er is een laadsessie actief.' })
    if (param == 'chargerName') and isinstance(value, str) and len(value) > 0:
        oppleoConfig.chargerName = value
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': value })

    # factorWhkm
    if (param == 'factorWhkm') and (isinstance(value, int) or RepresentsInt(value)):
        oppleoConfig.factorWhkm = int(value)
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': value })

    # chargerTariff
    # With an open charge session, there params are not allowed to change
    if (param == 'chargerTariff' and
        ChargeSessionModel.has_open_charge_session_for_device(oppleoConfig.chargerName)):
        return jsonify({ 'status': 409, 'param': param, 'reason': 'Er is een laadsessie actief.' })
    validation="^(?:0|[1-9][0-9]*)(?:[.][0-9]{1,2})?$"
    if (param == 'chargerTariff') and (isinstance(value, float) or RepresentsFloat(value)) and re.match(validation, value):
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

    # pushoverEnabled
    if (param == 'pushoverEnabled'):
        oppleoSystemConfig.pushoverEnabled = True if value.lower() in ['true', '1', 't', 'y', 'yes'] else False
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': oppleoSystemConfig.pushoverEnabled })

    # pushoverApiKey
    if (param == 'pushoverApiKey') and isinstance(value, str):
        oppleoSystemConfig.pushoverApiKey = value if len(value) > 0 else None
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': value })

    # pushoverUserKey
    if (param == 'pushoverUserKey') and isinstance(value, str):
        oppleoSystemConfig.pushoverUserKey = value if len(value) > 0 else None
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': value })

    # pushoverDevice
    if (param == 'pushoverDevice') and isinstance(value, str):
        oppleoSystemConfig.pushoverDevice = value if len(value) > 0 and value != '*' else None
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': value })

    # pushoverSound
    if (param == 'pushoverSound') and isinstance(value, str):
        oppleoSystemConfig.pushoverSound = value if len(value) > 0 else None
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': value })

    # mqttOutboundEnabled
    if (param == 'mqttOutboundEnabled'):
        oppleoSystemConfig.mqttOutboundEnabled = True if value.lower() in ['true', '1', 't', 'y', 'yes'] else False
        oppleoMqttClient = OppleoMqttClient()
        if oppleoMqttClient.is_connected() and not oppleoSystemConfig.mqttOutboundEnabled:
            oppleoMqttClient.disconnect()
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': oppleoSystemConfig.mqttOutboundEnabled })

    # mqttHost
    validation="^(((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.|$|((\/(3[0-2]|[012]?[0-9])){0,1})$)){4})$|^((?=.{1,255}$)[0-9A-Za-z](?:(?:[0-9A-Za-z]|-){0,61}[0-9A-Za-z])?(?:\.[0-9A-Za-z](?:(?:[0-9A-Za-z]|-){0,61}[0-9A-Za-z])?)*\.?)$"
    if (param == 'mqttHost') and isinstance(value, str) and re.match(validation, value):
        oppleoSystemConfig.mqttHost = value if len(value) > 0 else None
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': value })

     # mqttPort
    validation="^([0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])$"
    if (param == 'mqttPort') and isinstance(value, str) and re.match(validation, value):
        oppleoSystemConfig.mqttPort = value
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': oppleoSystemConfig.mqttPort })

    # mqttUsername
    if (param == 'mqttUsername') and isinstance(value, str):
        oppleoSystemConfig.mqttUsername = value if len(value) > 0 else None
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': value })

    # mqttPassword
    if (param == 'mqttPassword') and isinstance(value, str):
        oppleoSystemConfig.mqttPassword = value if len(value) > 0 else None
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
            # Announce switching off
            OutboundEvent.triggerEvent(
                event='vehicle_charge_status_stopped', 
                id=oppleoConfig.chargerName,
                namespace='/charge_session',
                public=False
                )
        else:
            # Enabling, also request update now
            oppleoConfig.vcsmThread.requestChargeStatusUpdate()
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': oppleoConfig.vehicleDataOnDashboard })

    # wakeupVehicleOnDataRequest
    if (param == 'wakeupVehicleOnDataRequest'):
        oppleoConfig.wakeupVehicleOnDataRequest = True if value.lower() in ['true', '1', 't', 'y', 'yes'] else False
        return jsonify({ 'status': HTTP_CODE_200_OK, 'param': param, 'value': oppleoConfig.wakeupVehicleOnDataRequest })


    # No parameter found or conditions not met
    return jsonify({ 'status': HTTP_CODE_404_NOT_FOUND, 'param': param, 'reason': 'Not found' })



# Always returns json
@flaskRoutes.route("/backup/<path:cmd>", defaults={'data': None}, strict_slashes=False, methods=["GET"])
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
# This function only requests the VehicleChargeStatusMonitorThread to obtain the charge state now, rather than to wait 
# to the next timout. The background task will submit the update through websockets.
@flaskRoutes.route("/request_vehicle_charge_state", methods=["GET"])
@flaskRoutes.route("/request_vehicle_charge_state/", methods=["GET"])
@authenticated_resource  # CSRF Token is valid
def requestVehicleChargeStatus():
    global oppleoConfig
    
    if oppleoConfig.vcsmThread is None:
        return jsonify({ 
            'status'        : HTTP_CODE_404_NOT_FOUND, 
            'id'            : oppleoConfig.chargerName, 
            'reason'        : 'No existing charge session'
            })

    oppleoConfig.vcsmThread.requestChargeStatusUpdate()
    return jsonify({ 
        'status'                    : HTTP_CODE_202_ACCEPTED
        })


# Always returns json
@flaskRoutes.route("/system_status/", methods=["GET"])
@authenticated_resource
def systemStatus():
    global flaskRoutesLogger, oppleoConfig
    flaskRoutesLogger.debug('/system_status/')

    return jsonify({
        'status'                    : HTTP_CODE_200_OK, 
        'restartRequired'           : (oppleoConfig.restartRequired or oppleoSystemConfig.restartRequired),
        'softwareUpdateInProgress'  : oppleoConfig.softwareUpdateInProgress,
        'startTime'                 : oppleoConfig.upSinceDatetimeStr,
        'backupInProgress'          : BackupUtil().backupInProgress,
        'odometerCaptureInProgress' : True if oppleoConfig.vuThread is not None and oppleoConfig.vuThread.is_alive() else False
        })


"""
    Each branch has a local and remote (origin) timestamp
    Each branch has (or not) a changelog.txt file with version number and date
    Local changelog.txt has a version and date, local active git branch has a timestamp
"""

# Always returns json
@flaskRoutes.route("/software_status", defaults={'branch': 'master'}, strict_slashes=False, methods=["GET"])
@flaskRoutes.route("/software_status/<path:branch>", methods=["GET"])
@flaskRoutes.route("/software_status/<path:branch>/", methods=["GET"])
@authenticated_resource  # CSRF Token is valid
def softwareStatus(branch='master'):
    global flaskRoutesLogger, oppleoConfig
    flaskRoutesLogger.debug('/software_status/{}'.format(branch))

    # Update status from github
    GitUtil.gitRemoteUpdate()
    branches = []
    availableReleaseSoftwareVersion = 'unknown'
    # Get the current branch structure
    (activeBranch, branchNames) = GitUtil.gitBranches()
    for branchName in branchNames:
        changeLogText = GitUtil.getChangeLogForBranch(branchName)
        parsedChangeLog = changeLog.parse(changeLogText=changeLogText)
        (versionNumber, versionDate) = changeLog.getMostRecentVersion(changeLogObj=parsedChangeLog)
        branches.append({
            'branch': branchName, 
            'version': str(versionNumber) if versionNumber is not None else '0.0.0', 
            'versionDate': changeLog.versionDateStr(versionDate=versionDate) if versionDate is not None else 'null', 
            'gitDate' : GitUtil.lastBranchGitDate(branch=branchName, remote=True)
            })
        if branchName == 'master':
            availableReleaseSoftwareVersion = str(versionNumber) if versionNumber is not None else '0.0.0'

    """
        softwareReleaseUpdateAvailable     if local and remote branch have different commit 
        softwareBuildUpdateAvailable       date of remote branch
    """
    return jsonify({
        'status': HTTP_CODE_200_OK, 
        'softwareReleaseUpdateAvailable'    : GitUtil.gitUpdateAvailable(),         # default on master
        'availableReleaseSoftwareDate'      : GitUtil.lastRemoteMasterGitDateStr(), # always on master
        'availableReleaseSoftwareVersion'   : availableReleaseSoftwareVersion,      # always on master
        'softwareBuildUpdateAvailable'      : GitUtil.gitUpdateAvailable(branch=activeBranch),
        'availableBuildSoftwareDate'        : GitUtil.lastBranchGitDateStr(branch=activeBranch, remote=True),
        'branches'                          : branches,
        'activeBranch'                      : activeBranch,
        'localGitDate'                      : GitUtil.lastBranchGitDate(branch=activeBranch, remote=False)
        })




@flaskRoutes.route("/account", defaults={'username': None, 'param': None, 'value': None}, strict_slashes=False, methods=["GET", "POST"])
@flaskRoutes.route("/account/", defaults={'username': None, 'param': None, 'value': None}, strict_slashes=False, methods=["GET", "POST"])
@flaskRoutes.route("/account/<path:username>", defaults={'param': None, 'value': None}, strict_slashes=False, methods=["GET", "POST"])
@flaskRoutes.route("/account/<path:username>/", defaults={'param': None, 'value': None}, strict_slashes=False, methods=["GET", "POST"])
@flaskRoutes.route("/account/<path:username>/<path:param>", methods=["GET"])
@flaskRoutes.route("/account/<path:username>/<path:param>/", methods=["GET"])
@flaskRoutes.route("/account/<path:username>/<path:param>/<path:value>", methods=["POST"])
@flaskRoutes.route("/account/<path:username>/<path:param>/<path:value>/", methods=["POST"])
@authenticated_resource  # CSRF Token is valid
def account(username:str=None, param:str=None, value:str=None):
    global flaskRoutesLogger, oppleoConfig, current_user

    flaskRoutesLogger.debug('/account{}/{}/{} {}'.format('username', param, value, request.method))

    # TODO now only allowed to change your own settings. Add admin rights later.

    if request.method == "GET":
        if username is None or param is None:
            return render_template("account.html", 
                oppleoconfig=oppleoConfig,
                changelog=changeLog,
                user=current_user
                )
        if param == 'enforceLocal2FA':
            return jsonify({
                'status'   : HTTP_CODE_200_OK,
                'username' : username,
                'param'    : param,
                'value'    : current_user.is_2FA_local_enforced()
                })
        return jsonify({
            'status'   : HTTP_CODE_404_NOT_FOUND, 
            'username' : username,
            'param'    : param,
            'msg'      : 'Parameter not found'
            })
    if request.method == "POST":
        if current_user.username != username:
            return jsonify({
                'status': HTTP_CODE_403_FORBIDDEN, 
                'msg'   : 'Changes to other users not allowed'
                })

        if param == 'enforceLocal2FA':
            current_user.enforce_local_2fa = True if value.lower() in ['true', '1', 't', 'y', 'yes'] else False
            current_user.save()
            return jsonify({
                'status': HTTP_CODE_200_OK,
                'username' : username,
                'param' : param,
                'value' : current_user.is_2FA_local_enforced()
                })

        if param == 'avatar':
            # check if the post request has the file part
            # if user does not select file, browser also submit an empty part without filename
            if 'value' not in request.files or request.files['value'].filename == '':
                return jsonify({
                    'status': HTTP_CODE_400_BAD_REQUEST,
                    'username' : username,
                    'param' : param,
                    'msg'   : 'No file uploaded'
                    })
            ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
            # Allowed extension?
            if (not '.' in request.files['value'].filename and 
                request.files['value'].filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS):
                return jsonify({
                    'status': HTTP_CODE_400_BAD_REQUEST,
                    'username' : username,
                    'param' : param,
                    'msg'   : 'Unsupported file type'
                    })
            # Determine unique and non-existing filename
            filename = None
            while filename is None or (os.path.exists(os.path.join(app.config['AVATAR_FOLDER'], filename))):
                filename = str(uuid.uuid4()) + '.' + request.files['value'].filename.rsplit('.', 1)[1].lower()
            # Save the avatar to it
            request.files['value'].save(os.path.join(app.config['AVATAR_FOLDER'], filename))
            user = User.get(username)
            # Remove current avatar - if not the default one
            if (user.avatar is not None and user.avatar != 'unknown.png'):
                try:
                    os.remove(app.config['AVATAR_FOLDER'] + user.avatar)
                except OSError:
                    pass
            user.avatar = filename
            user.save()
            return jsonify({
                'status'   : HTTP_CODE_200_OK,
                'username' : username,
                'param'    : param,
                'msg'      : 'Uploaded',
                'filename' : filename
                })

        return jsonify({
            'status'   : HTTP_CODE_404_NOT_FOUND, 
            'username' : username,
            'msg'      : 'Parameter not found'
            })

    return jsonify({
        'status': HTTP_CODE_404_NOT_FOUND, 
        'msg'   : 'Method {} not supported'.format(request.method)
        })
        


"""
    Flow enable:
        login, enable 2FA - enter password - gen shared_secret, store enc with pw
    Flow use:
        login - 2FA enabled? - ask pw + 2FA token - get secret and dec with pw, validate 2FA token
    Flow disable
        login, disable 2FA - enter password + 2FA key - valid: shared_secret->'', enable2FA->false

"""
@flaskRoutes.route("/enable_2FA", methods=["POST"])
@flaskRoutes.route("/enable_2FA/", methods=["POST"])
@authenticated_resource  # CSRF Token is valid
def enable_2FA():
    global flaskRoutesLogger, oppleoConfig

    flaskRoutesLogger.debug('/enable_2FA {}'.format(request.method))

    # For POST requests, process the json
    step = request.form.get('step')
    password = request.form.get('password')
    totp = request.form.get('totp')

    if step == 1 or step == '1':
        # Check the password
        if not check_password_hash(current_user.password, password):
            return jsonify({
                'status': HTTP_CODE_401_UNAUTHORIZED, 
                'step'  : 1,
                'code'  : DETAIL_CODE_25_PASSWORD_INCORRECT,
                'msg'   : 'Wachtwoord incorrect'
                })
        # Password correct, not already enabled?
        if current_user.has_enabled_2FA():
            # cannot re-enable
            return jsonify({
                'status'  : HTTP_CODE_400_BAD_REQUEST,
                'step'    : 1,
                'code'    : DETAIL_CODE_21_2FA_ENABLED,
                'msg'     : '2FA already enabled'
                })                
        # Password correct, generate secret and return - for now Google Authenticator only accepts 16 character secrets...
        secret_base32 = generateTotpSharedSecret()
        uri = keyUri(type='totp', secret=secret_base32, issuer='Oppleo ' + oppleoConfig.chargerName,
                        accountname=current_user.username)

        current_user.shared_secret = encryptAES(key=password, plainData=secret_base32)
        current_user.save()
        return jsonify({
            'status'  : HTTP_CODE_200_OK,
            'step'    : 1,
            'code'    : DETAIL_CODE_200_OK,
            'secret'  : secret_base32,
            'account' : 'Oppleo ' + oppleoConfig.chargerName + ' (' + current_user.username + ")",
            'type'    : 'totp',
            'url'     : uri
            })                
    if step == 2 or step == '2':
        # Check the password (again)
        if not check_password_hash(current_user.password, password):
            return jsonify({
                'status': HTTP_CODE_401_UNAUTHORIZED, 
                'step'  : 2,
                'code'  : DETAIL_CODE_25_PASSWORD_INCORRECT,
                'msg'   : 'Wachtwoord incorrect'
                })                
        # Password correct, validate the code
        shared_secret = decryptAES(key=password, encData=current_user.shared_secret)
        if validateTotp(totp=totp, shared_secret=shared_secret):
            # valid
            current_user.enabled_2fa = True
            current_user.save()
            # valid - 
            return jsonify({
                'status': HTTP_CODE_200_OK,
                'step'  : 2,
                'code'  : DETAIL_CODE_200_OK
                }) 
        # Not valid!
        return jsonify({
            'status': HTTP_CODE_400_BAD_REQUEST,
            'step'  : 2,
            'code'  : DETAIL_CODE_23_2FA_CODE_INCORRECT,
            'msg'   : 'Code not valid'
            }) 

    # Not valid!
    return jsonify({
        'status': HTTP_CODE_400_BAD_REQUEST,
        'step'  : 'unknown',
        'code'  : DETAIL_CODE_29_PROCESS_STEP_UNKNOWN,
        'msg'   : 'Proces step unknown'
        }) 


# TODO authorized
@flaskRoutes.route("/disable_2FA", methods=["POST"])
@flaskRoutes.route("/disable_2FA/", methods=["POST"])
@authenticated_resource  # CSRF Token is valid
def disable_2FA():
    global flaskRoutesLogger, oppleoConfig

    flaskRoutesLogger.debug('/disable_2FA {}'.format(request.method))

    # For POST requests, process the json
    step = request.form.get('step')
    password = request.form.get('password')
    totp = request.form.get('totp')

    if step == 1 or step == '1':
        # Check the password
        if not check_password_hash(current_user.password, password):
            return jsonify({
                'status': HTTP_CODE_401_UNAUTHORIZED,
                'code'  : DETAIL_CODE_25_PASSWORD_INCORRECT,
                'msg'   : 'Wachtwoord incorrect'
                })                
        # Password correct, 2FA enabled?
        if not current_user.has_enabled_2FA():
            # Cannot disable
            return jsonify({
                'status'  : HTTP_CODE_400_BAD_REQUEST,
                'step'    : 1,
                'code'    : DETAIL_CODE_20_2FA_NOT_ENABLED,
                'msg'     : '2FA not enabled'
                })         
        # valideer password en 2FA actief       
        return jsonify({
            'status'  : HTTP_CODE_200_OK,
            'step'    : 1,
            'code'    : DETAIL_CODE_200_OK
            })                
    if step == 2 or step == '2':
        # Check the password (again)
        if not check_password_hash(current_user.password, password):
            return jsonify({
                'status': HTTP_CODE_401_UNAUTHORIZED, 
                'code'  : DETAIL_CODE_25_PASSWORD_INCORRECT,
                'msg'   : 'Wachtwoord incorrect'
                })                
        # Password correct, validate the code
        shared_secret = decryptAES(key=password, encData=current_user.shared_secret)
        if validateTotp(totp=totp, shared_secret=shared_secret):
            # valid
            current_user.enabled_2fa = False
            current_user.save()
            # valid - 
            return jsonify({
                'status': HTTP_CODE_200_OK,
                'step'  : 2,
                'code'  : DETAIL_CODE_200_OK
                }) 
        # Not valid!
        return jsonify({
            'status': HTTP_CODE_400_BAD_REQUEST,
            'step'  : 2,
            'code'  : DETAIL_CODE_23_2FA_CODE_INCORRECT,
            'msg'   : 'Code not valid'
            }) 

    # Not valid!
    return jsonify({
        'status': HTTP_CODE_400_BAD_REQUEST,
        'step'  : 'unknown',
        'code'  : DETAIL_CODE_29_PROCESS_STEP_UNKNOWN,
        'msg'   : 'Proces step unknown'
        }) 



# https://stackoverflow.com/questions/7877282/how-to-send-image-generated-by-pil-to-browser
@flaskRoutes.route("/qr/<path:data>", methods=["GET"])
@flaskRoutes.route("/qr/<path:data>/", methods=["GET"])
@authenticated_resource  # CSRF Token is valid
def getRr(data:str=None):
    if data is None:
        abort(404)
    data = unquote(data)
    fill = request.args.get('fill', default='black', type=str)
    back = request.args.get('back', default='white', type=str)
    qr_img = makeQR(data=data, fill_color=fill, back_color=back)
    # qr_img.show()
    qr_io_buf = io.BytesIO()
    qr_img.save(qr_io_buf)
    qr_io_buf.seek(0)
  #  return send_file(qr_io_buf, mimetype='image/jpeg')
    try:
        return send_file(qr_io_buf,
                 attachment_filename='oppleo_qr.png',
                 mimetype='image/png',
                 cache_timeout=-1)
        
    except Exception as e:
        abort(404)



# https://stackoverflow.com/questions/7877282/how-to-send-image-generated-by-pil-to-browser
@flaskRoutes.route("/external_subnet/<path:subnetOrIP>", methods=["POST", "DELETE"])
@flaskRoutes.route("/external_subnet/<path:subnetOrIP>/", methods=["POST", "DELETE"])
@authenticated_resource  # CSRF Token is valid
def externalSubnet(subnetOrIP:str=None):
    if subnetOrIP is None:
        abort(404)
    subnetOrIP = unquote(subnetOrIP)
    subnetOrIP = IPv4.makeSubnet(subnetOrIP)
    if (request.method == 'POST'):
        ipList = oppleoConfig.routerIPAddress
        if (subnetOrIP in ipList):
            # Reject existing subnets
            return jsonify({
                'status'        : HTTP_CODE_303_SEE_OTHER,
                'subnetOrIP'    : subnetOrIP,
                'isSubnet'      : IPv4.validSubnet(subnetOrIP),
                'isSingleIP'    : IPv4.isSingleIP(subnetOrIP),
                'subnetOrIP32'  : IPv4.remove32Subnet(subnetOrIP),  # without /32 if IP
                'msg'           : 'Existing'
                })
        # New item, add to list
        ipList.append(subnetOrIP)
        oppleoConfig.routerIPAddress = ipList
        # Success
        return jsonify({
            'status'        : HTTP_CODE_200_OK,
            'subnetOrIP'    : subnetOrIP,
            'isSubnet'      : IPv4.validSubnet(subnetOrIP),
            'isSingleIP'    : IPv4.isSingleIP(subnetOrIP),
            'subnetOrIP32'  : IPv4.remove32Subnet(subnetOrIP),  # without /32 if IP
            'msg'           : 'Success'
            })

    if (request.method == 'DELETE'):
        ipList = oppleoConfig.routerIPAddress
        if (subnetOrIP not in ipList):
            # Reject non existing subnets
            return jsonify({
                'status'        : HTTP_CODE_404_NOT_FOUND,
                'subnetOrIP'    : subnetOrIP,
                'isSubnet'      : IPv4.validSubnet(subnetOrIP),
                'isIP'          : IPv4.isSingleIP(subnetOrIP),
                'subnetOrIP32'  : IPv4.remove32Subnet(subnetOrIP),  # without /32 if IP
                'msg'           : 'Not Found'
                })
        # Remove from list
        try:
            ipList.remove(subnetOrIP)
        except ValueError as ve:
            return jsonify({
                'status'        : HTTP_CODE_404_NOT_FOUND,
                'subnetOrIP'    : subnetOrIP,
                'isSubnet'      : IPv4.validSubnet(subnetOrIP),
                'isSingleIP'    : IPv4.isSingleIP(subnetOrIP),
                'subnetOrIP32'  : IPv4.remove32Subnet(subnetOrIP),  # without /32 if IP
                'msg'           : 'Not Found'
                })

        oppleoConfig.routerIPAddress = ipList
        # Success
        return jsonify({
            'status'        : HTTP_CODE_200_OK,
            'subnetOrIP'    : subnetOrIP,
            'isSubnet'      : IPv4.validSubnet(subnetOrIP),
            'isSingleIP'    : IPv4.isSingleIP(subnetOrIP),
            'subnetOrIP32'  : IPv4.remove32Subnet(subnetOrIP),  # without /32 if IP
            'msg'           : 'Success'
            }) 

    # Not valid!
    return jsonify({
        'status': HTTP_CODE_400_BAD_REQUEST,
        'code'  : DETAIL_CODE_28_ACTION_UNKNOWN,
        'action': request.method,
        'msg'   : 'Action unknown'
        }) 


# Always returns json
@flaskRoutes.route("/wakeup_vehicle", methods=["GET"])
@flaskRoutes.route("/wakeup_vehicle/", methods=["GET"])
@authenticated_resource
def wakeupVehicle():
    global flaskRoutesLogger, oppleoConfig
    flaskRoutesLogger.debug('/wakeup_vehicle/')

    """
        Which vehicle? Request how?
        - get current charge session
        - get current rfid
        - get vehicle
        - see if we can wake it up at all
        - wake up - takes long time, how to send to background?
        - send ok
    """

    if oppleoConfig.vcsmThread is None:
        return jsonify({
            'status': HTTP_CODE_400_BAD_REQUEST,
            'code'  : DETAIL_CODE_31_NO_ACTIVE_CHARGE_SESSION,
            'action': request.method,
            'msg'   : 'No active charge session'
            })

    oppleoConfig.vcsmThread.requestVehicleWakeup()
    return jsonify({ 
        'status': HTTP_CODE_202_ACCEPTED,
        'code'  : DETAIL_CODE_202_ACCEPTED,
        'action': request.method,
        'msg'   : 'Wakeup requested'
        })


# Always returns json
@flaskRoutes.route("/request_odometer_update", methods=["GET"])
@flaskRoutes.route("/request_odometer_update/", methods=["GET"])
@authenticated_resource
def requestOdometerUpdate():
    global flaskRoutesLogger, oppleoConfig

    flaskRoutesLogger.debug('/request_odometer_update/')

    chargeSession = ChargeSessionModel.getOpenChargeSession(device=oppleoConfig.chargerName)
    if chargeSession is None:
        return jsonify({
            'status': HTTP_CODE_400_BAD_REQUEST,
            'code'  : DETAIL_CODE_31_NO_ACTIVE_CHARGE_SESSION,
            'action': request.method,
            'msg'   : 'No active charge session'
            })
    uotu = UpdateOdometerTeslaUtil()
    uotu.charge_session_id = chargeSession.id
    uotu.condense = oppleoConfig.autoSessionCondenseSameOdometer
    # update_odometer takes some time, so put in own thread

    if oppleoConfig.vuThread is not None and oppleoConfig.vuThread.is_alive():
        # Thread (task) already running
        return jsonify({
            'status': HTTP_CODE_405_METHOD_NOT_ALLOWED,
            'code'  : DETAIL_CODE_47_TASK_ALREADY_RUNNING,
            'action': request.method,
            'msg'   : 'Already running'
            })

    oppleoConfig.vuThread = threading.Thread(target=uotu.update_odometer, name='TeslaUtilThread')
    oppleoConfig.vuThread.start()

    return jsonify({ 
        'status'        : HTTP_CODE_202_ACCEPTED,
        'code'          : DETAIL_CODE_202_ACCEPTED,
        'action'        : request.method,
        'msg'           : 'Requested',
        'chargeSession' : chargeSession.id,
        'condense'      : oppleoConfig.autoSessionCondenseSameOdometer
        })



# Always returns json
@flaskRoutes.route("/monthly_usage_overview", methods=["GET"])
@flaskRoutes.route("/monthly_usage_overview/", methods=["GET"])
@authenticated_resource
def monthlyUsageOverview():
    global oppleoConfig

    flaskRoutesLogger.debug('/monthly_usage_overview/')

    edmm = EnergyDeviceMeasureModel()
    edmm.energy_device_id = oppleoConfig.chargerName
    eme = edmm.get_end_month_energy_levels(oppleoConfig.chargerName)

    return jsonify(eme)

from nl.oppleo.services.PushMessage import PushMessage
from nl.oppleo.services.PushMessageProwl import PushMessageProwl
from nl.oppleo.services.PushMessagePushover import PushMessagePushover

from nl.oppleo.services.OppleoMqttClient import OppleoMqttClient 


# Always returns json
@flaskRoutes.route("/notification/<path:msgType>/", methods=["POST", "PUT"])
@flaskRoutes.route("/notification/<path:msgType>/", methods=["POST", "PUT"])
@authenticated_resource
def sendTestNotification(msgType:str=None):
    global flaskRoutesLogger, oppleoConfig
    flaskRoutesLogger.debug('/sendTestNotification {}'.format(type))

    message = request.form.get('message', default=None, type=str)
    if msgType is None or message is None:
        return jsonify({ 
            'status'    : HTTP_CODE_404_NOT_FOUND,
            'type'      : msgType if msgType is not None else '', 
            'message'   : message if message is not None else '' 
            })            

    if msgType.lower() == 'prowl':
        sendSuccess = PushMessageProwl.sendMessage(
            title='Oppleo ' + oppleoConfig.chargerName,
            message=message,
            priority=PushMessageProwl.priorityNormal,
            apiKey=oppleoSystemConfig.prowlApiKey,
            chargerName=oppleoConfig.chargerName
            )
        return jsonify({ 
            'status'        : HTTP_CODE_200_OK if sendSuccess else HTTP_CODE_424_FAILED_DEPENDENCY,
            'type'          : msgType.lower(),
            'message'       : message
            })            

    if msgType.lower() == 'pushover':
        sendSuccess = PushMessagePushover.sendMessage(
            title='Oppleo ' + oppleoConfig.chargerName, 
            message=message,
            priority=PushMessagePushover.priorityNormal,
            apiKey=oppleoSystemConfig.pushoverApiKey,
            userKey=oppleoSystemConfig.pushoverUserKey,
            device=oppleoSystemConfig.pushoverDevice,
            sound=oppleoSystemConfig.pushoverSound,
            chargerName=oppleoConfig.chargerName
            )
        return jsonify({ 
            'status'        : HTTP_CODE_200_OK if sendSuccess else HTTP_CODE_424_FAILED_DEPENDENCY,
            'type'          : msgType.lower(),
            'message'       : message
            })            

    if msgType.lower() == 'mqtt':
        oppleoMqttClient = OppleoMqttClient()
        topic = 'oppleo/' + oppleoSystemConfig.chargerName + '/notification'
        msg = {}
        msg['title'] = "Oppleo {}".format(oppleoConfig.chargerName)
        msg['message'] = message
        msg['priority'] = int(PushMessage.priorityNormal)
        sendSuccess = oppleoMqttClient.publish(topic=topic, message=json.dumps(msg), waitForPublish=True, timeout=1500)
        return jsonify({ 
            'status'        : HTTP_CODE_200_OK if sendSuccess else HTTP_CODE_424_FAILED_DEPENDENCY,
            'type'          : msgType.lower(),
            'message'       : message
            })            

    return jsonify({ 
        'status'    : HTTP_CODE_404_NOT_FOUND,
        'type'      : msgType if msgType is not None else '', 
        'message'   : message if message is not None else '' 
        })            
           



# Always returns json
@flaskRoutes.route("/pushover/<path:apiKey>/sounds", methods=["GET"])
@flaskRoutes.route("/pushover/<path:apiKey>/sounds/", methods=["GET"])
@authenticated_resource
def pushoverSounds(apiKey:str=None):
    global flaskRoutesLogger, oppleoConfig
    flaskRoutesLogger.debug('/pushover/{}/sounds/'.format(apiKey))

    soundList = PushMessagePushover.availableSounds(apiKey=apiKey)
    return jsonify({ 
        'status'        : HTTP_CODE_200_OK if soundList is not None else HTTP_CODE_404_NOT_FOUND,
        'apiKey'        : apiKey if apiKey is not None else '-', 
        'sounds'        : soundList if soundList is not None else {} 
        })            


# Always returns json
@flaskRoutes.route("/pushover/<path:userKey>/<path:apiKey>/devices", methods=["GET"])
@flaskRoutes.route("/pushover/<path:userKey>/<path:apiKey>/devices/", methods=["GET"])
@authenticated_resource
def pushoverDevices(userKey:str=None, apiKey:str=None):
    global flaskRoutesLogger, oppleoConfig
    flaskRoutesLogger.debug('/pushover/{}/{}/devices/'.format(userKey, apiKey))

    deviceList = PushMessagePushover.deviceList(userKey=userKey, apiKey=apiKey)

    return jsonify({ 
        'status'        : HTTP_CODE_200_OK if deviceList is not None else HTTP_CODE_404_NOT_FOUND,
        'userKey'       : userKey if userKey is not None else '-', 
        'apiKey'        : apiKey if apiKey is not None else '-', 
        'devices'       : deviceList if deviceList is not None else {} 
        })            


# Always returns json
@flaskRoutes.route("/mqtt/history", methods=["GET"])
@flaskRoutes.route("/mqtt/history/", methods=["GET"])
@flaskRoutes.route("/mqtt/history/<path:action>", methods=["POST"])
@flaskRoutes.route("/mqtt/history/<path:action>/", methods=["POST"])
@authenticated_resource
def mqttHistory(action:str=None):
    global flaskRoutesLogger, oppleoConfig
    flaskRoutesLogger.debug('/mqtt/history/')

    if oppleoConfig.mqttshThread is None:
        oppleoConfig.mqttshThread = MqttSendHistoryThread()

    if (request.method == 'GET' or not oppleoSystemConfig.mqttOutboundEnabled):
        # Return status
        return jsonify({ 
            'status'                : HTTP_CODE_200_OK,
            'mqttOutboundEnabled'   : oppleoSystemConfig.mqttOutboundEnabled,
            'details'               : oppleoConfig.mqttshThread.status
            })            

    if (action == "start"):
        # Start the process
        oppleoConfig.mqttshThread.mode = MqttSendHistoryThreadMode.MODE_TWO

        result = oppleoConfig.mqttshThread.start()
        return jsonify({ 
            'status'    : HTTP_CODE_200_OK if result["success"] else HTTP_CODE_409_CONFLICT,
            'action'    : action,
            'message'   : result["message"],
            'details'   : oppleoConfig.mqttshThread.status
            })

    if (action == "pause"):
        result = oppleoConfig.mqttshThread.pause()
        return jsonify({ 
            'status'    : HTTP_CODE_202_ACCEPTED if result["success"] else HTTP_CODE_409_CONFLICT,
            'action'    : action,
            'message'   : result["message"],
            'details'   : oppleoConfig.mqttshThread.status           
            })
    
    if (action == "cancel"):
        # Started or Paused , cancel the process
        result = oppleoConfig.mqttshThread.cancel()
        return jsonify({ 
            'status'    : HTTP_CODE_202_ACCEPTED if result["success"] else HTTP_CODE_409_CONFLICT,
            'action'    : action,
            'message'   : result["message"],
            'details'   : oppleoConfig.mqttshThread.status           
            })

    # Action not implemented
    return jsonify({ 
        'status'    : HTTP_CODE_400_BAD_REQUEST,
        'action'    : action
        })            

