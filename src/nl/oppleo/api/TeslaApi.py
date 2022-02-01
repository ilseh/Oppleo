from typing import Union, List, Any
import requests
import json
import time
import logging
import datetime
import random
import string
import os
from base64 import b64encode
from bs4 import BeautifulSoup   # HTML and XML parser
import urllib.parse


"""
    https://tesla-api.timdorr.com/api-basics/authentication
    https://github.com/fkhera/powerwallCloud/blob/master/powerwallBackup.py#L132
    
    Tesla uses a separate SSO service (auth.tesla.com) for authentication across their app and website (V3). Since feb 2021 the 
    previous (V2) authentication API is no longer operational. This V3 service is designed around a browser-based flow using 
    OAuth 2.0, but also appears to have support for Open ID Connect. This supports both obtaining an access token and refreshing 
    it as it expires.

    Tesla's SSO service has a WAF (web application firewall) that may temporarily block you if you make repeated, execessive requests.
    This is to prevent bots from attacking the service, either as a brute force or denial-of-service attack. This normally presents 
    a "challenge" page, which requires running some non-trivial JavaScript code to validate that you have a full browser engine 
    available. While you can potentially fully evaluate this page to remove the block, the best practice for now is to reduce your 
    calls to the SSO service to a minimum and avoid things like automatic request retries.

    vehicle_id vs id
    One potentially confusing part of Tesla's API is the switching use of the id and vehicle_id of the car. The id field is an identifier 
    for the car on the owner-api endpoint. The vehicle_id field is for identifying the car across different endpoints, such as the streaming 
    or Autopark APIs. For the state and command APIs, you should be using the id field. If your JSON parser doesn't support large numbers (>32 bit),
    then you can use the id_s field for a string version of the ID.

"""

class TeslaAPI:
    HTTP_TIMEOUT = 30

    # defining the api-endpoint  
    API_BASE = 'https://owner-api.teslamotors.com'
    API_AUTHENTICATION = '/oauth/token'  # POST

    API_AUTH_V3 = 'https://auth.tesla.com/oauth2/v3'
    API_AUTH_V3_REDIRECT_URI = 'https://auth.tesla.com/void/callback'
    API_AUTH_V3_AUTHORIZE = '/authorize'
    API_AUTH_V3_TOKEN = '/token'

    API_VEHICLES = '/api/1/vehicles'  # GET
    API_WAKE_UP = '/api/1/vehicles/{id}/wake_up'  # POST
    API_VEHICLE_STATE = '/api/1/vehicles/{id}/data_request/vehicle_state'  # GET
    API_CHARGE_STATE = '/api/1/vehicles/{id}/data_request/charge_state'  # GET
    API_CLIMATE_STATE = '/api/1/vehicles/{id}/data_request/climate_state'  # GET
    API_DRIVE_STATE = '/api/1/vehicles/{id}/data_request/drive_state'  # GET
    API_GUI_SETTINGS = '/api/1/vehicles/{id}/data_request/gui_settings'  # GET
    API_VEHICLE_CONFIG = '/api/1/vehicles/{id}/data_request/vehicle_config'  # GET
    API_MOBILE_ENABLED = '/api/1/vehicles/{id}/data_request/mobile_enabled'  # GET

    
    API_REVOKE = '/oauth/revoke'  # POST
    # All requests require a User-Agent header with any value provided.

    API_CODE_STATE_LENGTH_CHARS = 24
    API_CODE_VERIFIER_LENGTH_CHARS = 86

    API_AUTHENTICATION_GRANT_TYPE_PARAM = 'grant_type'
    API_AUTHENTICATION_GRANT_TYPE_PASSWORD = 'password'
    API_AUTHENTICATION_GRANT_TYPE_REFRESH_TOKEN = 'refresh_token'

    # https://tesla-api.timdorr.com/api-basics/authentication
    # https://www.teslaapi.io/
    # https://pastebin.com/pS7Z6yyP
    # https://github.com/adriankumpf/tesla_auth/blob/main/src/auth.rs
    # Stopped working approx 22nd feb 2020
 #   TESLA_CLIENT_ID = '81527cff06843c8634fdc09e8ac0abefb46ac849f38fe1e431c2ef2106796384'
 #   TESLA_CLIENT_SECRET = 'c7257eb71a564034f9419ee651c7d0e5f7aa6bfbd18bafb5c5c033b093bb2fa3'

    # https://github.com/timdorr/tesla-api/issues/79#issuecomment-419992028
    TESLA_CLIENT_ID = 'e4a9949fcfa04068f59abb5a658f2bac0a3428e4652315490b659d5ab3f35a9e'
    TESLA_CLIENT_SECRET = 'c75f14bbadc8bee3a7594412c31416f8300256d7668ea7e6e7f06727bfb9d220'

    HTTP_200_OK = 200
    HTTP_302_FOUND = 302    # When logged in, Tesla redirects to a non-existent URL
    HTTP_401_UNAUTHORIZED = 401
    HTTP_408_REQUEST_TIMEOUT = 408

    MAX_WAKE_UP_TRIES = 3
    VEHICLE_LIST_STATE_PARAM = 'state'
    VEHICLE_LIST_STATE_VALUE_ASLEEP = 'asleep'
    VEHICLE_LIST_STATE_VALUE_AWAKE = 'online'
    VEHICLE_LIST_STATE_VALUE_UNKNOWN = 'unknown'
    VEHICLE_LIST_ID_S_PARAM = 'id_s'
    VEHICLE_LIST_VEHICLE_ID_PARAM = 'vehicle_id'        # Should not be used in Oppleo!
    VEHICLE_LIST_DISPLAY_NAME_PARAM = 'display_name'
    VEHICLE_LIST_VIN_PARAM = 'vin'

    VEHICLE_DETAILS_ODOMETER_PARAM = 'odometer'

    VEHICLE_STATE_TOKEN = 'VEHICLE_STATE'
    CHARGE_STATE_TOKEN = 'CHARGE_STATE'
    CLIMATE_STATE_TOKEN = 'CLIMATE_STATE'
    DRIVE_STATE_TOKEN = 'DRIVE_STATE'
    VEHICLE_CONFIG_TOKEN = 'VEHICLE_CONFIG'

    access_token = None
    token_type = None
    created_at = None
    expires_in = None
    refresh_token = None

    got401Unauthorized = False

    vehicle_list = None

    def __init__(self):
        self.logger = logging.getLogger('nl.oppleo.api.TeslaAPI')
        self.logger.debug('TeslaApi.__init__')

    def reset(self):
        self.access_token = None
        self.token_type = None
        self.created_at = None
        self.expires_in = None
        self.refresh_token = None
        self.vehicle_list = None

    """ 
        A stable state value for requests, which is a random string of any length.
    """
    def generate_state(self):
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(self.API_CODE_STATE_LENGTH_CHARS))

    """
        Subsequent requests to the SSO service will require a "code verifier" and "code challenge". These are a random 
        86-character alphanumeric string and its SHA-256 hash encoded in URL-safe base64 (base64url). 

        Here is an example of generating them in Ruby, but you can apply this same process to other languages.            
            code_verifier = random_string(86)
            code_challenge = Base64.urlsafe_encode64(Digest::SHA256.hexdigest(code_verifier))

    """
    def generate_challenge(self):
        import base64
        from hashlib import sha256

        """
        verifier = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(self.API_CODE_VERIFIER_LENGTH_CHARS))
        challenge = base64.urlsafe_b64encode(sha256(verifier.encode('utf-8')).digest()).decode('utf-8')
        """

        verifier_bytes = os.urandom(32)
        challenge = base64.urlsafe_b64encode(verifier_bytes).rstrip(b'=')
        challenge_bytes = sha256(challenge).digest()
        challengeSum = base64.urlsafe_b64encode(challenge_bytes).rstrip(b'=')

        return verifier_bytes, challengeSum

    def generate_rnd(self, chars=43):
        letters = string.ascii_lowercase + string.ascii_uppercase + string.digits + "-" + "_"
        return "".join(random.choice(letters) for i in range(chars))        

    """ 
        Step 2: Get any hidden params from the session form, including session cookie, transaction_id and csrf
    """
    def authenticate_v3_getform(self, challenge, state, email):
        payload = {
            'client_id'             : 'ownerapi',
            'code_challenge'        : challenge,
            'code_challenge_method' : 'S256',
            'redirect_uri'          : self.API_AUTH_V3_REDIRECT_URI,
            'response_type'         : 'code',
            'scope'                 : 'openid email offline_access',
            'state'                 : state,
            'login_hint'            : email
        }
        session = requests.Session()
        try:
            r = session.get(
                url=self.API_AUTH_V3 +
                    self.API_AUTH_V3_AUTHORIZE,
                params=payload,
                timeout=self.HTTP_TIMEOUT
                )
        except requests.exceptions.ConnectTimeout as ct:
            self.logger.warn("TeslaAPI.authenticate_v3_getform(): ConnectTimeout (>{}s)".format(self.HTTP_TIMEOUT))
            return None, None
        except requests.ReadTimeout as rt:
            self.logger.warn("TeslaAPI.authenticate_v3_getform(): ReadTimeout (>{}s)".format(self.HTTP_TIMEOUT))
            return None, None

        self.logger.debug("Result {} - {} ".format(r.status_code, r.reason))
        if r.status_code != self.HTTP_200_OK:
            self.logger.warn("TeslaAPI.authenticate_v3_getform(): status code {}".format(r.status_code))
            return None, None
        self.logger.debug("TeslaAPI.authenticate_v3_getform(): status code {} text: {}".format(r.status_code, r.text))

        session_params = {}
        soup = BeautifulSoup(r.text, features="html.parser")
        # Known tags
        for tag in ['_csrf', '_phase', '_process', 'transaction_id', 'cancel']:
            # Cannot find for the name directly, as name is the key for the tag itself (input here)
            try:
                session_params[tag] = soup.find(name="input", attrs={"name": tag})['value']
            except: # Field does not exist
                pass
        # Hidden tags (includes the known)
        hidden_tags = soup.find_all("input", type="hidden")
        for tag in hidden_tags:
            # tag.name refers to input, not the name attribute of the input field
            # therefor session_params[tag.name] = tag.value doesn't work
            # also for some reason checking if ('name' in tag) returns False, while tag exist. Hence Exception catch.
            try:
                session_params[tag['name']] = tag['value']
            except KeyError as ke:
                pass

        return session, session_params


    def auth_post(self, data, grant_type_param_value) -> bool:
        try:
            r = requests.post(
                url=self.API_BASE +
                    self.API_AUTHENTICATION + '?' +
                    self.API_AUTHENTICATION_GRANT_TYPE_PARAM + '=' +
                    grant_type_param_value,
                data=data,
                timeout=self.HTTP_TIMEOUT
            )
        except requests.exceptions.ConnectTimeout as ct:
            self.logger.warn("TeslaAPI.auth_post(): ConnectTimeout (>{}s)".format(self.HTTP_TIMEOUT))
            return False
        except requests.ReadTimeout as rt:
            self.logger.warn("TeslaAPI.auth_post(): ReadTimeout (>{}s)".format(self.HTTP_TIMEOUT))
            return False

        self.logger.debug("Result {} - {} ".format(r.status_code, r.reason))
        if r.status_code != self.HTTP_200_OK:
            self.logger.warn("TeslaAPI.auth_post(): status code {}".format(r.status_code))
            if r.text is not None:
                self.logger.warn("TeslaAPI.auth_post(): status code {} text: {}".format(r.status_code, r.text))
            if r.status_code == self.HTTP_401_UNAUTHORIZED:
                self.got401Unauthorized = True
            return False
        self.got401Unauthorized = False

        # extracting response text
        response_dict = json.loads(r.text)
        self.access_token = response_dict['access_token']
        self.token_type = response_dict['token_type']
        self.created_at = response_dict['created_at']
        self.expires_in = response_dict['expires_in']
        self.refresh_token = response_dict['refresh_token']

        self.logger.debug(
            "{\n  'access_token': '%s',\n  'token_type': '%s',\n  'created_at': '%s',\n  'expires_in': '%s',"
            "\n  'refresh_token': '%s'\n}" %
            (self.access_token, self.token_type, self.created_at, self.expires_in, self.refresh_token))
        return True

    """ 
        Step 3: Login and obtain authorization code
    """
    def authorization_v3_get_auth_code(self, challenge, session_params, session, state):
        # Untill march 2021 this header should be included. After it no longer is required and now the POST requests times out when 
        # using this header
        # headers = {
        #     'User-Agent' : 'PowerwallDarwinManager' 
        # }
        hdrform = {
            'client_id'             : 'ownerapi',
            'code_challenge'        : challenge,
            'code_challenge_method' : 'S256',
            'redirect_uri'          : self.API_AUTH_V3_REDIRECT_URI,
            'response_type'         : 'code',
            'scope'                 : 'openid email offline_access',
            'state'                 : state
        }
        try:
            r = session.post(
                url=self.API_AUTH_V3 +
                    self.API_AUTH_V3_AUTHORIZE +
                    '?' +
                    urllib.parse.urlencode(hdrform),
                # headers=headers,
                data=session_params,
                allow_redirects=False,
                timeout=self.HTTP_TIMEOUT
            )
        except requests.exceptions.ConnectTimeout as ct:
            self.logger.warn("TeslaAPI.authorization_v3_get_auth_code(): ConnectTimeout (>{}s)".format(self.HTTP_TIMEOUT))
            return None
        except requests.ReadTimeout as rt:
            self.logger.warn("TeslaAPI.authorization_v3_get_auth_code(): ReadTimeout (>{}s)".format(self.HTTP_TIMEOUT))
            return None

        # HTTP 302 Found is returned if correct username/password is given (don't follow the redirect).
        # HTTP 200 OK is returned if no username/password is given.
        # HTTP 401 Unauthorized is returned if incorrect username/password is given.
        self.logger.debug("Result {} - {} ".format(r.status_code, r.reason))
        if r.status_code != self.HTTP_302_FOUND:
            self.logger.warn("TeslaAPI.authorization_v3_get_auth_code(): status code {}".format(r.status_code))
            if r.status_code == self.HTTP_401_UNAUTHORIZED:
                self.got401Unauthorized = True
            return None
        self.got401Unauthorized = False

        # TODO - implement MFA
        is_mfa = True if r.status_code == 200 and "/mfa/verify" in r.text else False

        auth_code = None
        try:
            parsed = urllib.parse.urlparse(r.headers["Location"])
            auth_code = urllib.parse.parse_qs(parsed.query)['code'][0]
        except Exception as e:
            pass

        return auth_code

    """ 
        Step 4: Get bearer token using authentication code
    """
    def authorization_v3_get_bearer_token(self, session, auth_code, code_verifier):
        # Untill march 2021 this header should be included. After it no longer is required and now the POST requests times out when 
        # using this header
        # headers = {
        #     'User-Agent' : 'PowerwallDarwinManager' 
        # }
        payload = {
            'grant_type'    : 'authorization_code',
            'client_id'     : 'ownerapi',
            'code'          : auth_code,
            'code_verifier' : self.generate_rnd(108), # code_verifier
            'redirect_uri'  : self.API_AUTH_V3_REDIRECT_URI
        }
        try:
            r = session.post(
                url=self.API_AUTH_V3 +
                    self.API_AUTH_V3_TOKEN,
                # headers=headers,
                data=payload,
                timeout=self.HTTP_TIMEOUT
            )
        except requests.exceptions.ConnectTimeout as ct:
            self.logger.warn("TeslaAPI.authorization_v3_get_bearer_token(): ConnectTimeout (>{}s)".format(self.HTTP_TIMEOUT))
            return None
        except requests.ReadTimeout as rt:
            self.logger.warn("TeslaAPI.authorization_v3_get_bearer_token(): ReadTimeout (>{}s)".format(self.HTTP_TIMEOUT))
            return None

        self.logger.debug("Result {} - {} ".format(r.status_code, r.reason))
        if r.status_code != self.HTTP_200_OK:
            self.logger.warn("TeslaAPI.new_bearer_token(): status code {}".format(r.status_code))
            if r.status_code == self.HTTP_401_UNAUTHORIZED:
                self.got401Unauthorized = True
            return None
        self.got401Unauthorized = False

        bearer_token = None
        try:
            bearer_token = r.json()["access_token"]
        except Exception as e:
            pass
        return bearer_token

 
    """ 
        Step 5: Get an access_token with expiry date etc using bearer token
    """
    def authorization_v3_get_access_token(self, session, bearer_token) -> bool:
        # Untill march 2021 the 'PowerwallDarwinManager' User-Agent header should be included. After it no longer is required and 
        # now the POST requests times out when using this header
        headers = {
            # 'User-Agent' : 'PowerwallDarwinManager',
            'authorization' : 'bearer ' + bearer_token
        }
        payload = {
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "client_id": self.TESLA_CLIENT_ID,
        }
        try:
            r = session.post(
                url=self.API_BASE +
                    self.API_AUTHENTICATION,
                headers=headers,
                data=payload,
                timeout=self.HTTP_TIMEOUT
            )
        except requests.exceptions.ConnectTimeout as ct:
            self.logger.warn("TeslaAPI.authorization_v3_get_access_token(): ConnectTimeout (>{}s)".format(self.HTTP_TIMEOUT))
            return False
        except requests.ReadTimeout as rt:
            self.logger.warn("TeslaAPI.authorization_v3_get_access_token(): ReadTimeout (>{}s)".format(self.HTTP_TIMEOUT))
            return False

        self.logger.debug("Result {} - {} ".format(r.status_code, r.reason))
        if r.status_code != self.HTTP_200_OK:
            self.logger.warn("TeslaAPI.new_access_token(): status code {}".format(r.status_code))
            if r.status_code == self.HTTP_401_UNAUTHORIZED:
                self.got401Unauthorized = True
            return False
        self.got401Unauthorized = False

        try:
            response_json = r.json()
            # extracting response text
            response_dict = json.loads(r.text)
            self.access_token = response_dict['access_token']
            self.token_type = response_dict['token_type']
            self.created_at = response_dict['created_at']
            self.expires_in = response_dict['expires_in']
            self.refresh_token = response_dict['refresh_token']
        except Exception as e:
            return False
        return True

    """
        This method gets the form, obtains the cookie and possible hidden fields, submits a login form to 
        emulate a web browser.

    """
    def authenticate_v3(self, email=None, password=None) -> bool:

        # Step 1: Generate a state (random string, static during this cycle) and verifier
        state = self.generate_state()
        code_verifier, challenge = self.generate_challenge()

        # Step 2: Get any hidden params from the session form, including session cookie, transaction_id and csrf
        session, session_params = self.authenticate_v3_getform(challenge=challenge, state=state, email=email)
        if session is None or session_params is None:
            # Connection timeout or error, could not even get the form
            return False

        # Step 3: Login and obtain authorization code
        # Add credentials
        session_params['identity'] = email
        session_params['credential'] = password
        # Submit login form
        auth_code = self.authorization_v3_get_auth_code(session=session,                \
                                                        challenge=challenge,            \
                                                        session_params=session_params,  \
                                                        state=state
                                                    )
        if (self.got401Unauthorized or auth_code is None):
            # Not authorized
            return False

        # Step 4: Get bearer token using authentication code
        bearer_token = self.authorization_v3_get_bearer_token(session=session,               \
                                                              code_verifier=code_verifier,   \
                                                              auth_code=auth_code            \
                                                            )
        if (self.got401Unauthorized or bearer_token is None):
            # Not authorized
            return False

        # Step 5: Get an access_token with expiry date etc using bearer token
        result = self.authorization_v3_get_access_token(session=session,           \
                                                        bearer_token=bearer_token  \
                                                    )

        return result


    def authenticate(self, email=None, password=None):
        self.logger.debug('authenticate() ' + self.API_AUTHENTICATION)
        if email is None or password is None:
            self.logger.debug('Credentials to obtain token missing.')
            return False

        data = {
            "grant_type": self.API_AUTHENTICATION_GRANT_TYPE_PASSWORD,
            "client_id": self.TESLA_CLIENT_ID,
            "client_secret": self.TESLA_CLIENT_SECRET,
            "email": email,
            "password": password
        }

        # 01 - Authenticate [POST]
        # sending post request and saving response as response object 
        return self.auth_post(data, self.API_AUTHENTICATION_GRANT_TYPE_PASSWORD)

    def getVehicleList(self, update=False):
        self.logger.debug("getVehicleList() update={}".format(str(update)))
        if (self.vehicle_list != None and not update):
            self.logger.debug("getVehicleList() return existing vehicle_list")
            return self.vehicle_list
        # Reset
        self.logger.debug("getVehicleList() reset vehicle_list")
        self.vehicle_list = None
        if not self.hasValidToken():
            return self.vehicle_list
        # 02 - Vehicles [GET]
        # If >1 then show list and select, otherwise pick the vehicle  
        # sending post request and saving response as response object
        try:
            r = requests.get(
                url=self.API_BASE + self.API_VEHICLES,
                headers={'Authorization': self.token_type + ' ' + self.access_token},
                timeout=self.HTTP_TIMEOUT
            )
        except requests.exceptions.ConnectTimeout as ct:
            self.logger.warn("TeslaAPI.getVehicleList(): ConnectTimeout (>{}s)".format(self.HTTP_TIMEOUT))
            return None
        except requests.ReadTimeout as rt:
            self.logger.warn("TeslaAPI.getVehicleList(): ReadTimeout (>{}s)".format(self.HTTP_TIMEOUT))
            return None

        self.logger.debug("Result {} - {} ".format(r.status_code, r.reason))
        if r.status_code != self.HTTP_200_OK:
            self.logger.warn("TeslaAPI.getVehicleList(): status code {}".format(r.status_code))
            if r.status_code == self.HTTP_401_UNAUTHORIZED:
                self.got401Unauthorized = True
            return None
        self.got401Unauthorized = False

        response_dict = json.loads(r.text)
        self.logger.debug("Vehicle count : %s " % response_dict['count'])
        self.vehicle_list = response_dict['response']
        for vehicle in self.vehicle_list:
            self.logger.debug("Het {} (given vehicle name) is : {} ".format(self.VEHICLE_LIST_DISPLAY_NAME_PARAM,  vehicle[self.VEHICLE_LIST_DISPLAY_NAME_PARAM]))
            self.logger.debug("Het {} is : {} ".format(self.VEHICLE_LIST_ID_S_PARAM,  vehicle[self.VEHICLE_LIST_ID_S_PARAM]))
            self.logger.debug("Het {} is : {} ".format(self.VEHICLE_LIST_STATE_PARAM,  vehicle[self.VEHICLE_LIST_STATE_PARAM]))
            self.logger.debug("Het {} is : {} ".format(self.VEHICLE_LIST_VEHICLE_ID_PARAM,  vehicle[self.VEHICLE_LIST_VEHICLE_ID_PARAM]))
            self.logger.debug("Het {} is : {} ".format(self.VEHICLE_LIST_VIN_PARAM,  vehicle[self.VEHICLE_LIST_VIN_PARAM]))
        return self.vehicle_list

    def getVehicleWithId(self, id:str=None, update:bool=False):
        self.logger.debug("getVehicleWithId() id={}".format(id))
        if id is None:
            self.logger.debug("getVehicleWithId() id={} return None (1)".format(id))
            return None
        vehicle_list = self.getVehicleList(update=update)
        if vehicle_list is None:
            self.logger.debug("getVehicleWithId() id={} return None (2)".format(id))
            return None
        for vehicle in vehicle_list:
            if id == vehicle[self.VEHICLE_LIST_ID_S_PARAM]:
                self.logger.debug("%d vehicles, selected vehicle id %s" % (len(vehicle_list), id))
                return vehicle
        return None

    def getVehicleNameIdList(self):
        self.logger.debug("getVehicleNameIdList")
        vehicle_list = self.getVehicleList()
        if vehicle_list is None:
            return []  # Empty list
        nid = []
        for vehicle in vehicle_list:
            nid.append({
                'id': vehicle[self.VEHICLE_LIST_ID_S_PARAM],
                'name': vehicle[self.VEHICLE_LIST_DISPLAY_NAME_PARAM],
                'vin': vehicle[self.VEHICLE_LIST_VIN_PARAM]
            })
        return nid


    def wakeUpVehicleWithId(self, id:str=None, update:bool=False, wakeupTries:int=0):
        self.logger.debug("wakeUpVehicleWithId(): id={}".format(id))
        vehicle = self.getVehicleWithId(id=id, update=update)
        if vehicle is None:
            return False
        wake_up_tries = 0
        while ((vehicle[self.VEHICLE_LIST_STATE_PARAM] == self.VEHICLE_LIST_STATE_VALUE_ASLEEP) and
               (wake_up_tries < (wakeupTries if wakeupTries != 0 else self.MAX_WAKE_UP_TRIES))):
            wake_up_tries += 1
            # 03 Wake it up, otherwise the STATE call will timeout
            try:
                r = requests.post(
                    url=self.API_BASE + self.API_WAKE_UP.replace('{id}', vehicle[self.VEHICLE_LIST_ID_S_PARAM]),
                    headers={'Authorization': self.token_type + ' ' + self.access_token},
                    timeout=self.HTTP_TIMEOUT
                )
                self.logger.debug("Result {} - {} ".format(r.status_code, r.reason))
                if r.status_code != self.HTTP_200_OK:
                    self.logger.warn("TeslaAPI.wakeUpVehicleWithId(): status code {}".format(r.status_code))
                    if r.status_code == self.HTTP_401_UNAUTHORIZED:
                        self.got401Unauthorized = True
                    return False
                self.got401Unauthorized = False

                response_dict = json.loads(r.text)
                vehicle[self.VEHICLE_LIST_STATE_PARAM] = response_dict['response'][self.VEHICLE_LIST_STATE_PARAM]
                self.logger.debug(
                    "On try %d the state is now %s " % (wake_up_tries, vehicle[self.VEHICLE_LIST_STATE_PARAM]))
                if vehicle[self.VEHICLE_LIST_STATE_PARAM] == self.VEHICLE_LIST_STATE_VALUE_AWAKE:
                    return True
                self.logger.debug("Wait 5 seconds to try again...")
                time.sleep(5)
            except requests.exceptions.ConnectTimeout as ct:
                self.logger.warn("TeslaAPI.wakeUpVehicleWithId(): ConnectTimeout (>{}s)".format(self.HTTP_TIMEOUT))
                # Continue loop
            except requests.ReadTimeout as rt:
                self.logger.warn("TeslaAPI.wakeUpVehicleWithId(): ReadTimeout (>{}s)".format(self.HTTP_TIMEOUT))
                # Continue loop

        if ((vehicle[self.VEHICLE_LIST_STATE_PARAM] == self.VEHICLE_LIST_STATE_VALUE_ASLEEP) and
                (wake_up_tries >= self.MAX_WAKE_UP_TRIES)):
            self.logger.debug("Could not wake up the car...")
            return False
        return True


    def vehicleWithIdIsAsleep(self, id:str=None, update:bool=False):
        self.logger.debug("vehicleWithIdIsAsleep() id={}".format(id))
        vehicle = self.getVehicleWithId(id=id, update=update)
        if vehicle is None:
            self.logger.debug("Cannot determine. Vehicle not found.")
            return False
        self.logger.debug("Vehicle state {}.".format(vehicle[self.VEHICLE_LIST_STATE_PARAM]))
        return vehicle[self.VEHICLE_LIST_STATE_PARAM] == self.VEHICLE_LIST_STATE_VALUE_ASLEEP


    def getVehicleStateWithId(self, id:str=None, update:bool=False):
        self.logger.debug("getVehicleStateWithId() id={} update={}".format(id, str(update)))
        vehicle = self.getVehicleWithId(id=id, update=update)
        if id is None or vehicle is None:
            self.logger.debug("getVehicleStateWithId() id={}  return None (1)".format(id))
            return None
        # Existing?
        if (self.VEHICLE_STATE_TOKEN in vehicle) and (vehicle[self.VEHICLE_STATE_TOKEN] != None) and (not update):
            return vehicle[self.VEHICLE_STATE_TOKEN]
        # Needs to be awake
        if (self.vehicleWithIdIsAsleep(id=id) and
                not self.wakeUpVehicleWithId(id=id)):
            self.logger.debug("getVehicleStateWithId() id={}  return None (2)".format(id))
            return None
        self.logger.debug("getVehicleStateWithId() - awake")
        url = self.API_BASE + self.API_VEHICLE_STATE.replace('{id}', id)
        self.logger.debug("getVehicleStateWithId() - %s" % url)
        # 04 Get the milage
        try:
            r = requests.get(
                url=url,
                headers={'Authorization': self.token_type + ' ' + self.access_token},
                timeout=self.HTTP_TIMEOUT
            )
        except requests.exceptions.ConnectTimeout as ct:
            self.logger.warn("TeslaAPI.getVehicleStateWithId(): ConnectTimeout (>{}s)".format(self.HTTP_TIMEOUT))
            return None
        except requests.ReadTimeout as rt:
            self.logger.warn("TeslaAPI.getVehicleStateWithId(): ReadTimeout (>{}s)".format(self.HTTP_TIMEOUT))
            return None

        self.logger.debug("Result {} - {} ".format(r.status_code, r.reason))
        if r.status_code != self.HTTP_200_OK:
            self.logger.warn("TeslaAPI.getVehicleStateWithId(): status code {}".format(r.status_code))
            if r.status_code == self.HTTP_408_REQUEST_TIMEOUT:
                response_dict = json.loads(r.text)
                self.logger.warning("Error: %s" % response_dict['error'])
            if r.status_code == self.HTTP_401_UNAUTHORIZED:
                self.got401Unauthorized = True
            return None
        self.got401Unauthorized = False

        response_dict = json.loads(r.text)
        vehicle[self.VEHICLE_STATE_TOKEN] = response_dict['response']
        self.logger.debug("Odometer : %s [miles]" % response_dict['response'][self.VEHICLE_DETAILS_ODOMETER_PARAM])
        return response_dict['response']


    def getChargeStateWithId(self, id:str=None, update:bool=False, wakeUpWhenSleeping:bool=False):
        self.logger.debug("getChargeStateWithId() id={} update={}".format(id, str(update)))
        # Get updated vehicle info, as iit contains state (sleep or online)
        vehicle = self.getVehicleWithId(id=id, update=update)
        if id is None or vehicle is None:
            self.logger.debug("getChargeStateWithId() id={}  return None (1)".format(id))
            return None
        # Existing?
        if (self.CHARGE_STATE_TOKEN in vehicle) and (vehicle[self.CHARGE_STATE_TOKEN] != None) and (not update):
            return vehicle[self.CHARGE_STATE_TOKEN]
        # Needs to be awake
        if ( ( self.vehicleWithIdIsAsleep(id=id) and not wakeUpWhenSleeping) or
             ( wakeUpWhenSleeping and not self.wakeUpVehicleWithId(id=id) )
           ):
           # Not awake and not requested to not succeded to wakeup
            self.logger.debug("getChargeStateWithId() id={}  return None (2)".format(id))
            return None
        self.logger.debug("getChargeStateWithId() - awake")
        url = self.API_BASE + self.API_CHARGE_STATE.replace('{id}', id)
        self.logger.debug("getChargeStateWithId() - %s" % url)
        # 04 Get the milage
        try:
            r = requests.get(
                url=url,
                headers={'Authorization': self.token_type + ' ' + self.access_token},
                timeout=self.HTTP_TIMEOUT
            )
        except requests.exceptions.ConnectTimeout as ct:
            self.logger.warn("TeslaAPI.getChargeStateWithId(): ConnectTimeout (>{}s)".format(self.HTTP_TIMEOUT))
            return None
        except requests.ReadTimeout as rt:
            self.logger.warn("TeslaAPI.getChargeStateWithId(): ReadTimeout (>{}s)".format(self.HTTP_TIMEOUT))
            return None

        self.logger.debug("Result {} - {} ".format(r.status_code, r.reason))
        if r.status_code != self.HTTP_200_OK:
            self.logger.warn("TeslaAPI.getChargeStateWithId(): status code {}".format(r.status_code))
            if r.status_code == self.HTTP_408_REQUEST_TIMEOUT:
                # NOTE this happens when the vehicle is unreachable or still sleeping (undetected)
                response_dict = json.loads(r.text)
                self.logger.warning("Error: %s" % response_dict['error'])
            if r.status_code == self.HTTP_401_UNAUTHORIZED:
                self.got401Unauthorized = True
            return None
        self.got401Unauthorized = False

        response_dict = json.loads(r.text)
        vehicle[self.CHARGE_STATE_TOKEN] = response_dict['response']
        return response_dict['response']


    def getClimateStateWithId(self, id:str=None, update:bool=False):
        self.logger.debug("getClimateStateWithId() id={} update={}".format(id, str(update)))
        vehicle = self.getVehicleWithId(id=id, update=update)
        if id is None or vehicle is None:
            self.logger.debug("getClimateStateWithId() id={}  return None (1)".format(id))
            return None
        # Existing?
        if (self.CLIMATE_STATE_TOKEN in vehicle) and (vehicle[self.CLIMATE_STATE_TOKEN] != None) and (not update):
            return vehicle[self.CLIMATE_STATE_TOKEN]
        # Needs to be awake
        if (self.vehicleWithIdIsAsleep(id=id) and
                not self.wakeUpVehicleWithId(id=id)):
            self.logger.debug("getClimateStateWithId() id={}  return None (2)".format(id))
            return None
        self.logger.debug("getClimateStateWithId() - awake")
        url = self.API_BASE + self.API_CLIMATE_STATE.replace('{id}', id)
        self.logger.debug("getClimateStateWithId() - %s" % url)
        # 04 Get the milage
        try:
            r = requests.get(
                url=url,
                headers={'Authorization': self.token_type + ' ' + self.access_token},
                timeout=self.HTTP_TIMEOUT
            )
        except requests.exceptions.ConnectTimeout as ct:
            self.logger.warn("TeslaAPI.getClimateStateWithId(): ConnectTimeout (>{}s)".format(self.HTTP_TIMEOUT))
            return None
        except requests.ReadTimeout as rt:
            self.logger.warn("TeslaAPI.getClimateStateWithId(): ReadTimeout (>{}s)".format(self.HTTP_TIMEOUT))
            return None

        self.logger.debug("Result {} - {} ".format(r.status_code, r.reason))
        if r.status_code != self.HTTP_200_OK:
            self.logger.warn("TeslaAPI.getClimateStateWithId(): status code {}".format(r.status_code))
            if r.status_code == self.HTTP_408_REQUEST_TIMEOUT:
                response_dict = json.loads(r.text)
                self.logger.warning("Error: %s" % response_dict['error'])
            if r.status_code == self.HTTP_401_UNAUTHORIZED:
                self.got401Unauthorized = True
            return None
        self.got401Unauthorized = False

        response_dict = json.loads(r.text)
        vehicle[self.CLIMATE_STATE_TOKEN] = response_dict['response']
        return response_dict['response']


    def getDriveStateWithId(self, id:str=None, update:bool=False):
        self.logger.debug("getDriveStateWithId() id={} update={}".format(id, str(update)))
        vehicle = self.getVehicleWithId(id=id, update=update)
        if id is None or vehicle is None:
            self.logger.debug("getDriveStateWithId() id={}  return None (1)".format(id))
            return None
        # Existing?
        if (self.DRIVE_STATE_TOKEN in vehicle) and (vehicle[self.DRIVE_STATE_TOKEN] != None) and (not update):
            return vehicle[self.DRIVE_STATE_TOKEN]
        # Needs to be awake
        if (self.vehicleWithIdIsAsleep(id=id) and
                not self.wakeUpVehicleWithId(id=id)):
            self.logger.debug("getDriveStateWithId() id={}  return None (2)".format(id))
            return None
        self.logger.debug("getDriveStateWithId() - awake")
        url = self.API_BASE + self.API_DRIVE_STATE.replace('{id}', id)
        self.logger.debug("getDriveStateWithId() - %s" % url)
        # 04 Get the milage
        try:
            r = requests.get(
                url=url,
                headers={'Authorization': self.token_type + ' ' + self.access_token},
                timeout=self.HTTP_TIMEOUT
            )
        except requests.exceptions.ConnectTimeout as ct:
            self.logger.warn("TeslaAPI.getDriveStateWithId(): ConnectTimeout (>{}s)".format(self.HTTP_TIMEOUT))
            return None
        except requests.ReadTimeout as rt:
            self.logger.warn("TeslaAPI.getDriveStateWithId(): ReadTimeout (>{}s)".format(self.HTTP_TIMEOUT))
            return None

        self.logger.debug("Result {} - {} ".format(r.status_code, r.reason))
        if r.status_code != self.HTTP_200_OK:
            self.logger.warn("TeslaAPI.getDriveStateWithId(): status code {}".format(r.status_code))
            if r.status_code == self.HTTP_408_REQUEST_TIMEOUT:
                response_dict = json.loads(r.text)
                self.logger.warning("Error: %s" % response_dict['error'])
            if r.status_code == self.HTTP_401_UNAUTHORIZED:
                self.got401Unauthorized = True
            return None
        self.got401Unauthorized = False

        response_dict = json.loads(r.text)
        vehicle[self.DRIVE_STATE_TOKEN] = response_dict['response']
        return response_dict['response']


    def getVehicleConfigWithId(self, id:str=None, update:bool=False):
        self.logger.debug("getVehicleConfigWithId() id={} update={}".format(id, str(update)))
        vehicle = self.getVehicleWithId(id=id, update=update)
        if id is None or vehicle is None:
            self.logger.debug("getVehicleConfigWithId() id={}  return None (1)".format(id))
            return None
        # Existing?
        if (self.VEHICLE_CONFIG_TOKEN in vehicle) and (vehicle[self.VEHICLE_CONFIG_TOKEN] != None) and (not update):
            return vehicle[self.VEHICLE_CONFIG_TOKEN]
        # Needs to be awake
        if (self.vehicleWithIdIsAsleep(id=id) and
                not self.wakeUpVehicleWithId(id=id)):
            self.logger.debug("getVehicleConfigWithId() id={}  return None (2)".format(id))
            return None
        self.logger.debug("getVehicleConfigWithId() - awake")
        url = self.API_BASE + self.API_VEHICLE_CONFIG.replace('{id}', id)
        self.logger.debug("getVehicleConfigWithId() - %s" % url)
        # 04 Get the milage
        try:
            r = requests.get(
                url=url,
                headers={'Authorization': self.token_type + ' ' + self.access_token},
                timeout=self.HTTP_TIMEOUT
            )
        except requests.exceptions.ConnectTimeout as ct:
            self.logger.warn("TeslaAPI.getVehicleConfigWithId(): ConnectTimeout (>{}s)".format(self.HTTP_TIMEOUT))
            return None
        except requests.ReadTimeout as rt:
            self.logger.warn("TeslaAPI.getVehicleConfigWithId(): ReadTimeout (>{}s)".format(self.HTTP_TIMEOUT))
            return None

        self.logger.debug("Result {} - {} ".format(r.status_code, r.reason))
        if r.status_code != self.HTTP_200_OK:
            self.logger.warn("TeslaAPI.getVehicleConfigWithId(): status code {}".format(r.status_code))
            if r.status_code == self.HTTP_408_REQUEST_TIMEOUT:
                response_dict = json.loads(r.text)
                self.logger.warning("Error: %s" % response_dict['error'])
            if r.status_code == self.HTTP_401_UNAUTHORIZED:
                self.got401Unauthorized = True
            return None
        self.got401Unauthorized = False

        response_dict = json.loads(r.text)
        vehicle[self.VEHICLE_CONFIG_TOKEN] = response_dict['response']
        return response_dict['response']


    def getOdometerWithId(self, id=None):
        self.logger.debug("getOdometerWithId() id={}".format(id))
        if id is None:
            self.logger.debug("getOdometerWithId() return None (1)")
            return None
        vehicle_details = self.getVehicleStateWithId(id)
        if vehicle_details is None:
            self.logger.debug("getOdometerWithId() return None (2)")
            return None
        odometer = vehicle_details[self.VEHICLE_DETAILS_ODOMETER_PARAM]
        self.logger.debug("getOdometerWithId() odometer value = {} (miles)".format(odometer))
        odometerKm = round(float(odometer) * 1.609344)
        self.logger.debug("getOdometerWithId() odometer km value = {}".format(odometerKm))
        return odometerKm

    def refreshToken(self):
        self.logger.debug('refreshToken() ' + self.API_AUTHENTICATION)
        if self.refresh_token is None:
            self.logger.debug('Refresh token missing.')
            return False
        data = {
            "grant_type": self.API_AUTHENTICATION_GRANT_TYPE_REFRESH_TOKEN,
            "client_id": self.TESLA_CLIENT_ID,
            "client_secret": self.TESLA_CLIENT_SECRET,
            "refresh_token": self.refresh_token
        }
        # 01 - Authenticate [POST]
        # sending post request and saving response as response object
        return self.auth_post(data, self.API_AUTHENTICATION_GRANT_TYPE_REFRESH_TOKEN)

    def revokeToken(self) -> bool:
        self.logger.debug("revokeToken()")

        if self.access_token is None:
            self.logger.debug("No access_token to revoke")
            return False

        data = {
            "token": self.access_token
        }
        try:
            r = requests.post(
                url=self.API_BASE + self.API_REVOKE,
                data=data,
                timeout=self.HTTP_TIMEOUT
            )
        except requests.exceptions.ConnectTimeout as ct:
            self.logger.warn("TeslaAPI.revokeToken(): ConnectTimeout (>{}s)".format(self.HTTP_TIMEOUT))
            return False
        except requests.ReadTimeout as rt:
            self.logger.warn("TeslaAPI.revokeToken(): ReadTimeout (>{}s)".format(self.HTTP_TIMEOUT))
            return False

        self.logger.debug("Result {} - {} ".format(r.status_code, r.reason))
        if r.status_code != self.HTTP_200_OK:
            self.logger.warn("TeslaAPI.revokeToken(): status code {}, NOT successfull REVOKING TOKEN".format(r.status_code))
            if r.status_code == self.HTTP_401_UNAUTHORIZED:
                self.got401Unauthorized = True
            return False
        self.got401Unauthorized = False

        self.reset()
        return True


    # Token can expire, but apparently the token can also just become invalid.
    # Not sure if the refresh token in that case will still work.
    def hasValidToken(self) -> bool:
        self.logger.debug("hasValidToken()")
        if self.access_token is None or self.token_type is None:
            self.logger.debug("hasValidToken() Token ({}) is None or TokenType ({}) is None".format(self.access_token, self.token_type))
            return False
        # Ran into 401's last time?
        if self.got401Unauthorized:
            self.logger.debug("Ran into 401 Unauthorized")
            return False
        date = datetime.datetime.fromtimestamp(int(self.created_at) + int(self.expires_in))  # / 1e3
        today = date.today()
        if date > today:
            self.logger.debug("token is still valid")
            return True
        self.logger.debug("token has expired")
        return False


    # Token valid for 45 days, refresh if token is valid for less than 31 days
    # Does not refresh token!
    def tokenRequiresRefresh(self):
        self.logger.debug("tokenRequiresRefresh()")
        if not self.hasValidToken():
            self.logger.debug("tokenRequiresRefresh() token is not valid")
            # Report update if there is an invalid access_token
            return False
        token_date = datetime.datetime.fromtimestamp(
            int(self.created_at) + int(self.expires_in)
        )  # / 1e3
        today = datetime.datetime.now()
        delta = datetime.timedelta(days=31)
        if today > (token_date - delta):
            self.logger.debug("tokenRequiresRefresh() - Needs refresh")
            return True
        self.logger.debug("tokenRequiresRefresh() - Token does not need refreshing yet")
        return False


    # Token valid for 45 days, refresh if token is valid for less than 31 days
    # returns True if token was refreshed
    def refreshTokenIfRequired(self):
        self.logger.debug("refreshTokenIfRequired()")
        if not self.hasValidToken():
            self.logger.debug("refreshTokenIfRequired() - token is not valid")
            # Report update if there is an invalid access_token
            return False
        token_date = datetime.datetime.fromtimestamp(
            int(self.created_at) + int(self.expires_in)
        )  # / 1e3
        today = datetime.datetime.now()
        delta = datetime.timedelta(days=31)
        if today > (token_date - delta):
            self.logger.debug("refreshTokenIfRequired() - Needs refresh")
            return self.refreshToken()
        self.logger.debug("refreshTokenIfRequired() - Token does not need refreshing yet")
        return False