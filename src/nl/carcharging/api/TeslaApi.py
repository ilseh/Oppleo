import requests
import json
import time
import logging
import datetime


class TeslaAPI:
    # defining the api-endpoint  
    API_BASE = 'https://owner-api.teslamotors.com'
    API_AUTHENTICATION = '/oauth/token'  # POST
    API_VEHICLES = '/api/1/vehicles'  # GET
    API_WAKE_UP = '/api/1/vehicles/{id}/wake_up'  # POST
    API_VEHICLE_STATE = '/api/1/vehicles/{id}/data_request/vehicle_state'  # GET
    API_REVOKE = '/oauth/revoke'  # POST
    # All requests require a User-Agent header with any value provided.

    API_AUTHENTICATION_GRANT_TYPE_PARAM = 'grant_type'
    API_AUTHENTICATION_GRANT_TYPE_PASSWORD = 'password'
    API_AUTHENTICATION_GRANT_TYPE_REFRESH_TOKEN = 'refresh_token'

    # https://tesla-api.timdorr.com/api-basics/authentication
    # https://www.teslaapi.io/
    # https://pastebin.com/pS7Z6yyP
    # Stopped working approx 22nd feb 2020
    TESLA_CLIENT_ID = '81527cff06843c8634fdc09e8ac0abefb46ac849f38fe1e431c2ef2106796384'
    TESLA_CLIENT_SECRET = 'c7257eb71a564034f9419ee651c7d0e5f7aa6bfbd18bafb5c5c033b093bb2fa3'

    # https://github.com/timdorr/tesla-api/issues/79#issuecomment-419992028
    #TESLA_CLIENT_ID = 'e4a9949fcfa04068f59abb5a658f2bac0a3428e4652315490b659d5ab3f35a9e'
    #TESLA_CLIENT_SECRET = 'c75f14bbadc8bee3a7594412c31416f8300256d7668ea7e6e7f06727bfb9d220'

    HTTP_200_OK = 200
    HTTP_401_UNAUTHORIZED = 401
    HTTP_408_REQUEST_TIMEOUT = 408

    MAX_WAKE_UP_TRIES = 3
    VEHICLE_LIST_STATE_PARAM = 'state'
    VEHICLE_LIST_STATE_VALUE_ASLEEP = 'asleep'
    VEHICLE_LIST_STATE_VALUE_AWAKE = 'online'
    VEHICLE_LIST_STATE_VALUE_UNKNOWN = 'unknown'
    VEHICLE_LIST_ID_PARAM = 'id_s'
    VEHICLE_LIST_DISPLAY_NAME_PARAM = 'display_name'
    VEHICLE_LIST_VIN_PARAM = 'vin'

    VEHICLE_DETAILS_ODOMETER_PARAM = 'odometer'

    VEHICLE_DETAILS_TOKEN = 'DETAILS_FROM_API_CALL'

    access_token = None
    token_type = None
    created_at = None
    expires_in = None
    refresh_token = None

    got401Unauthorized = False

    vehicle_list = None

    def __init__(self):
        self.logger = logging.getLogger('nl.carcharging.api.TeslaAPI')
        self.logger.debug('TeslaApi.__init__')

    def reset(self):
        self.access_token = None
        self.token_type = None
        self.created_at = None
        self.expires_in = None
        self.refresh_token = None
        self.vehicle_list = None

    def auth_post(self, data, grant_type_param_value):
        r = requests.post(
            url=self.API_BASE +
                self.API_AUTHENTICATION + '?' +
                self.API_AUTHENTICATION_GRANT_TYPE_PARAM + '=' +
                grant_type_param_value,
            data=data
        )
        self.logger.debug("Result {} - {} ".format(r.status_code, r.reason))
        if r.status_code != self.HTTP_200_OK:
            self.logger.warn("TeslaAPI.auth_post(): status code {}".format(r.status_code))
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
        self.logger.debug("getVehicleList: " + self.API_VEHICLES)
        if (self.vehicle_list != None and not update):
            return self.vehicle_list
        # Reset
        self.vehicle_list = None
        # 02 - Vehicles [GET]
        # If >1 then show list and select, otherwise pick the vehicle  
        # sending post request and saving response as response object 
        r = requests.get(
            url=self.API_BASE + self.API_VEHICLES,
            headers={'Authorization': self.token_type + ' ' + self.access_token}
        )
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
            self.logger.debug(
                "The display_name (given vehicle name) is : %s " % vehicle[self.VEHICLE_LIST_DISPLAY_NAME_PARAM])
            self.logger.debug("Het id_s is : %s " % vehicle[self.VEHICLE_LIST_ID_PARAM])
            self.logger.debug("Het state is : %s " % vehicle[self.VEHICLE_LIST_STATE_PARAM])
            self.logger.debug("Het vehicle_id is : %s " % vehicle['vehicle_id'])
            self.logger.debug("Het VIN is : %s " % vehicle['vin'])
        return self.vehicle_list

    def getVehicleWithId(self, id=None):
        self.logger.debug("getVehicleWithId")
        if id is None:
            return None
        vehicle_list = self.getVehicleList()
        if vehicle_list is None:
            self.logger.debug("vehicle_list is None")
            return None
        for vehicle in vehicle_list:
            if id == vehicle[self.VEHICLE_LIST_ID_PARAM]:
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
                'id': vehicle[self.VEHICLE_LIST_ID_PARAM],
                'name': vehicle[self.VEHICLE_LIST_DISPLAY_NAME_PARAM],
                'vin': vehicle[self.VEHICLE_LIST_VIN_PARAM]
            })
        return nid


    def wakeUpVehicleWithId(self, id=None):
        self.logger.debug("wakeUpVehicleWithId: " + self.API_WAKE_UP)
        vehicle = self.getVehicleWithId(id)
        if vehicle is None:
            return False
        wake_up_tries = 0
        while ((vehicle[self.VEHICLE_LIST_STATE_PARAM] == self.VEHICLE_LIST_STATE_VALUE_ASLEEP) and
               (wake_up_tries < self.MAX_WAKE_UP_TRIES)):
            wake_up_tries += 1
            # 03 Wake it up, otherwise the STATE call will timeout
            r = requests.post(
                url=self.API_BASE + self.API_WAKE_UP.replace('{id}', vehicle[self.VEHICLE_LIST_ID_PARAM]),
                headers={'Authorization': self.token_type + ' ' + self.access_token}
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

        if ((vehicle[self.VEHICLE_LIST_STATE_PARAM] == self.VEHICLE_LIST_STATE_VALUE_ASLEEP) and
                (wake_up_tries >= self.MAX_WAKE_UP_TRIES)):
            self.logger.debug("Could not wake up the car...")
            return False
        return True


    def vehicleWithIdIsAsleep(self, id=None):
        self.logger.debug("vehicleWithIdIsAsleep()")
        vehicle = self.getVehicleWithId(id)
        if vehicle is None:
            self.logger.debug("Cannot determine. Vehicle not found.")
            return False
        self.logger.debug("Vehicle state {}.".format(vehicle[self.VEHICLE_LIST_STATE_PARAM]))
        return vehicle[self.VEHICLE_LIST_STATE_PARAM] == self.VEHICLE_LIST_STATE_VALUE_ASLEEP


    def getVehicleDetailsWithId(self, id=None, update=False):
        self.logger.debug("getVehicleDetailsWithId()")
        vehicle = self.getVehicleWithId(id)
        if id is None or vehicle is None:
            return None
        # Existing?
        if (self.VEHICLE_DETAILS_TOKEN in vehicle) and (vehicle[self.VEHICLE_DETAILS_TOKEN] != None) and (not update):
            return vehicle[self.VEHICLE_DETAILS_TOKEN]
        # Needs to be awake
        if (self.vehicleWithIdIsAsleep(id) and
                not self.wakeUpVehicleWithId(id)):
            return None
        self.logger.debug("getVehicleDetailsWithId() - awake")
        url = self.API_BASE + self.API_VEHICLE_STATE.replace('{id}', id)
        self.logger.debug("getVehicleDetailsWithId() - %s" % url)
        # 04 Get the milage
        r = requests.get(
            url=url,
            headers={'Authorization': self.token_type + ' ' + self.access_token}
        )
        self.logger.debug("Result {} - {} ".format(r.status_code, r.reason))
        if r.status_code != self.HTTP_200_OK:
            self.logger.warn("TeslaAPI.getVehicleDetailsWithId(): status code {}".format(r.status_code))
            if r.status_code == self.HTTP_408_REQUEST_TIMEOUT:
                response_dict = json.loads(r.text)
                self.logger.warning("Error: %s" % response_dict['error'])
            if r.status_code == self.HTTP_401_UNAUTHORIZED:
                self.got401Unauthorized = True
            return None
        self.got401Unauthorized = False

        response_dict = json.loads(r.text)
        vehicle[self.VEHICLE_DETAILS_TOKEN] = response_dict['response']
        self.logger.debug("Odometer : %s [miles]" % response_dict['response'][self.VEHICLE_DETAILS_ODOMETER_PARAM])
        return response_dict['response']

    def getOdometerWithId(self, id=None):
        self.logger.debug("getOdometerWithId()")
        if id is None:
            return None
        vehicle_details = self.getVehicleDetailsWithId(id)
        if vehicle_details is None:
            return None
        return round(float(vehicle_details[self.VEHICLE_DETAILS_ODOMETER_PARAM]) * 1.609344)

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

    def revokeToken(self):
        self.logger.debug("revokeToken()")

        if self.access_token is None:
            self.logger.debug("No access_token to revoke")
            return False

        data = {
            "token": self.access_token
        }
        r = requests.post(
            url=self.API_BASE + self.API_REVOKE,
            data=data
        )
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
    def hasValidToken(self):
        self.logger.debug("hasValidToken()")
        if self.access_token is None:
            self.logger.debug("token is None")
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
    def tokenRefreshCheck(self):
        self.logger.debug("token_refresh_check()")
        if not self.hasValidToken():
            self.logger.debug("token is not valid")
            # Report update if there is an invalid access_token
            return self.access_token is not None
        token_date = datetime.datetime.fromtimestamp(
            int(self.created_at) + int(self.expires_in)
        )  # / 1e3
        today = datetime.datetime.now()
        delta = datetime.timedelta(days=31)
        if today > (token_date - delta):
            self.logger.debug("Needs refresh")
            return self.refreshToken()
        self.logger.debug("Token does not need refreshing yet")
        return False
