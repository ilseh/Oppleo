import logging
import teslapy
from oauthlib.oauth2.rfc6749.errors import UnauthorizedClientError, MissingCodeError

from nl.oppleo.models.KeyValueStoreModel import KeyValueStoreModel

"""
    https://github.com/tdorssers/TeslaPy

    The package teslapy stores accounts (in cache.json) based on tesla account. Issue when two rfid cards are linked to the same account, or 
    one account has multiple vehicles per card.
    Solution is a kvstore per rfid token.

"""


class TeslaPyWrapper:
    __KVSTORE = 'teslapy'
    __logger = None
    __rfid = None       # Rfid unique key
    __email = None

    def __init__(self, rfid:str=None, email:str=None):
        self.__logger = logging.getLogger('nl.oppleo.api.TeslaPyWrapper')
        self.__logger.debug('TeslaPyWrapper.__init__')
        self.__rfid=rfid
        self.__email=email

    """
        format is a dict with email keys, and a json body
            {
                "url": "https://auth.tesla.com/",
                "sso": {
                    "access_token": "123",
                    "refresh_token": "abc",
                    "id_token": "ABC",
                    "expires_in": 28800,
                    "token_type": "Bearer",
                    "expires_at": 1644431335.62566
                }
            }
    """
    def __teslapy_loader(self):
        if self.__rfid is None:
            self.__logger.error('__teslapy_loader - No rfid id to use as scope to obtain cache with!')
            # return empty cache
            return {}
        kvstore = KeyValueStoreModel.get_scope(kvstore=self.__KVSTORE, scope=self.__rfid)
        cache = {}
        for kvobj in kvstore:
            cache[kvobj.key] = kvobj.value
        return cache

    def __teslapy_dumper(self, cache):
        if self.__rfid is None:
            self.__logger.error('__teslapy_loader - No rfid id as scope object to write cache with!')

        stored_cache = self.__teslapy_loader()
        # Generate diff
        to_delete = list(set(stored_cache) - set(cache))
        to_add = list(set(cache) - set(stored_cache))
        to_update = list(set(cache) & set(stored_cache))

        # Run through to-delete keys
        for email in to_delete:
            self.__logger.info('__teslapy_dumper - delete kvstore={} scope={} email={}'.format(self.__KVSTORE, self.__rfid, email))
            kvs = KeyValueStoreModel.get_value(kvstore=self.__KVSTORE, scope=self.__rfid, key=email)
            kvs.delete()

        # Run through to-add keys
        for email in to_add:
            self.__logger.info('__teslapy_dumper - add kvstore={} scope={} email={}'.format(self.__KVSTORE, self.__rfid, email))
            kvs = KeyValueStoreModel(kvstore=self.__KVSTORE, scope=self.__rfid, key=email, value=cache[email])
            kvs.save()

        # Run through to-update keys
        for email in to_update:
            self.__logger.info('__teslapy_dumper - update kvstore={} scope={} email={}'.format(self.__KVSTORE, self.__rfid, email))
            kvs = KeyValueStoreModel.get_value(kvstore=self.__KVSTORE, scope=self.__rfid, key=email)
            kvs.value=cache[email]
            kvs.save()


    def authorizeByRefreshToken(self, email:str=None, refresh_token:str=None, rfid:str=None) -> bool:
        if email is None:
            email = self.__email
        if email is None:
            self.__logger.warn("tpwAuthorizeByRefreshToken() - Cannot authorize - no email.")
            return False
        if rfid is not None:
            self.__rfid = rfid
        if self.__rfid is None:
            self.__logger.warn("tpwAuthorizeByRefreshToken() - Cannot authorize - no rfid.")
            return False
        # Establish account
        teslaPy = teslapy.Tesla(email, cache_loader=self.__teslapy_loader, cache_dumper=self.__teslapy_dumper)
        # Set the refresh token
        try:
            teslaPy.refresh_token(refresh_token=refresh_token)
        except (UnauthorizedClientError, MissingCodeError, Exception) as e:
            # Invalid refresh token
            return False
        return True


    def getAuthorizationUrl(self, email:str=None) -> str:
        if email is None:
            email = self.__email
        if email is None:
            self.__logger.warn("tpwGetAuthorizationUrl() - Cannot create url for email {}.".format(email))
            return
        # Establish account
        teslaPy = teslapy.Tesla(email, cache_loader=self.__teslapy_loader, cache_dumper=self.__teslapy_dumper)
        return teslaPy.authorization_url()


    def authorizeByUrl(self, email:str=None, url:str=None, rfid:str=None) -> bool:
        if email is None:
            email = self.__email
        if email is None:
            self.__logger.warn("authorizeByUrl() - Cannot authorize - no email.")
            return
        if rfid is not None :
            self.__rfid = rfid
        if self.__rfid is None:
            self.__logger.warn("authorizeByUrl() - Cannot authorize - no rfid.")
            return False        # Establish account
        teslaPy = teslapy.Tesla(email, cache_loader=self.__teslapy_loader, cache_dumper=self.__teslapy_dumper)
        # Set the refresh token
        try:
            teslaPy.fetch_token(authorization_response=url)
        except (UnauthorizedClientError, MissingCodeError, Exception) as e:
            # Invalid URL
            return False
        return True



    def isAuthorized(self, email:str=None) -> bool:
        if email is None:
            email = self.__email
        if email is None:
            self.__logger.warn("isAuthorized() - Cannot identify authorization status for email {}.".format(email))
            return
        teslaPy = teslapy.Tesla(email, cache_loader=self.__teslapy_loader, cache_dumper=self.__teslapy_dumper)    
        authorized = teslaPy.authorized
        return authorized


    """
        Does not wake up vehicle
    """
    def getVehicleList(self, email:str=None, max_retries:int=3):
        if email is None:
            email = self.__email
        if email is None:
            self.__logger.warn("getVehicleList() - Cannot get vehicle list for email {}.".format(email))
            return []

        teslaPy = teslapy.Tesla(email, cache_loader=self.__teslapy_loader, cache_dumper=self.__teslapy_dumper)
        if not teslaPy.authorized:
            self.__logger.warn("getVehicleList() - Email {} not authorizd".format(email))
            return []

        return teslaPy.vehicle_list()



    """
        Does not wake up vehicle
    """
    def getVehicle(self, email:str=None, vin:str=None, max_retries:int=3):
        if email is None:
            email = self.__email
        if email is None:
            self.__logger.warn("getVehicle() - Cannot get vehicle list for email {}.".format(email))
            return None

        teslaPy = teslapy.Tesla(email, cache_loader=self.__teslapy_loader, cache_dumper=self.__teslapy_dumper)
        if not teslaPy.authorized:
            self.__logger.warn("getVehicle() - Email {} not authorizd".format(email))
            return None

        vehicle_list = teslaPy.vehicle_list()
        for vehicle_from_list in vehicle_list:
            if vehicle_from_list['vin'] == vin:
                return vehicle_from_list

        self.__logger.warn("getVehicle() - Found {} vehicles, none with vin {}".format(len(vehicle_list), vin))
        return None


    """
        Does not wake up vehicle
    """
    def isAwake(self, email:str=None, vin:str=None) -> bool:
        if email is None:
            email = self.__email
        if email is None:
            self.__logger.warn("isAwake() - Cannot find vehicle - no email.")
            return False

        vehicle = self.getVehicle(email, vin)
        return vehicle is not None and vehicle['state'] != 'asleep'



    def getVehicleData(self, email:str=None, vin:str=None, max_retries:int=3, wake_up:bool=False):
        if email is None:
            email = self.__email
        if email is None:
            self.__logger.warn("getVehicleData() - Cannot get vehicle data for email {}.".format(email))
            return

        teslaPy = teslapy.Tesla(email, cache_loader=self.__teslapy_loader, cache_dumper=self.__teslapy_dumper)
        if not teslaPy.authorized:
            self.__logger.warn("getVehicleData() - Email {} not authorizd".format(email))
            return None

        vehicle_list = teslaPy.vehicle_list()
        vehicle = None
        for vehicle_from_list in vehicle_list:
            if vehicle_from_list['vin'] == vin:
                vehicle = vehicle_from_list
        if vehicle is None:
            self.__logger.warn("getVehicleData() - Found {} vehicles, none with vin {}".format(len(vehicle_list), vin))
            return None
        # Does not have to be online for summary
        # vehicle_summary = vehicle.get_vehicle_summary()
        # Are we waking up?
        if vehicle['state'] == 'asleep' and not wake_up:
            self.__logger.info("getVehicleData() - vehicle sleeping and requested to not wake up. No vehicle data obtained")
            return None

        vehicle_data = None
        tries = 1
        while vehicle_data is None and tries <= max_retries:
            # Vehicle asleep?
            if vehicle['state'] == 'asleep':
                vehicle.sync_wake_up()
            try:
                vehicle_data = vehicle.get_vehicle_data()
            except Exception as e: 
                # Timeout?
                if e.response.status_code == 408:
                    self.__logger.info("getVehicleData() - timeout {}".format(tries))
                if e.response.status_code != 408:
                    # Something else, forget it
                    self.__logger.warn("getVehicleData() - error {}".format(e))
                    tries = max_retries
            tries += 1

        if vehicle_data is None:
            self.__logger.warn("getVehicleData() - could not retrieve vehicle data for {}".format(vin))
            return None

        return vehicle_data


    """
        Grab specific information from the vehicle data, in this case the odometer value
    """

    def getOdometer(self, email:str=None, vin:str=None, max_retries:int=3, wake_up:bool=True) -> int:
        if email is None:
            email = self.__email
        if email is None:
            self.__logger.warn("getOdometer() - Cannot get vehicle data for email {}.".format(email))
            return -1

        # Wakeup required for odometer value
        vehicle_data = self.getVehicleData(email=email, vin=vin, max_retries=max_retries, wake_up=wake_up)

        if vehicle_data is None:
            self.__logger.warn("getOdometer() - could not retrieve odometer value for {}".format(vin))
            return -1

        odometerInMiles = vehicle_data.get('vehicle_state', {}).get('odometer', None)
        odometerInKm = round(float(odometerInMiles) * 1.609344) if odometerInMiles is not None else None
        self.__logger.debug("getOdometer() - odometer: {}M or {}km".format(odometerInMiles, odometerInKm))

        return odometerInKm


    def getChargeState(self, email:str=None, vin:str=None, max_retries:int=3, wake_up:bool=False) -> dict:
        if email is None:
            email = self.__email
        if email is None:
            self.__logger.warn("getChargeState() - Cannot get vehicle data for email {}.".format(email))
            return {}

        vehicle_data = self.getVehicleData(email=email, vin=vin, max_retries=max_retries, wake_up=wake_up)

        if vehicle_data is None:
            self.__logger.warn("getChargeState() - could not retrieve charge state for {}".format(vin))
            return {}

        return vehicle_data.get('charge_state', {})


    """
        Logout clears the token
    """
    def logout(self, email:str=None):
        if email is None:
            email = self.__email
        if email is None:
            self.__logger.warn("logout() - Cannot get vehicle data for email {}.".format(email))
            return None

        teslaPy = teslapy.Tesla(email, cache_loader=self.__teslapy_loader, cache_dumper=self.__teslapy_dumper)
        return teslaPy.logout(sign_out=True)
