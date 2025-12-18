import asyncio
import json
import logging
from dataclasses import asdict
from datetime import datetime, date

from pypolestar import PolestarApi
from pypolestar.auth import PolestarAuth

from nl.oppleo.models.RfidModel import RfidModel
from nl.oppleo.models.KeyValueStoreModel import KeyValueStoreModel


class PolestarPyWrapper:
    __KVSTORE = 'pypolestar'
    __logger = None
    __username = None       # Rfid unique key
    __api = None
    __rfid = None
    

    def __init__(self, rfid:str=None, username:str=None):
        self.__logger = logging.getLogger(self.__class__.__module__)
        self.__logger.debug('PolestarPyWrapper.__init__')
        self.__rfid = rfid
        self.__username = username


    def __pypolestar_loader(self):
        if self.__rfid is None:
            self.__logger.error('__pypolestar_loader - No rfid id to use as scope to obtain cache with!')
            # return empty cache
            return {}
        kvstore = KeyValueStoreModel.get_scope(kvstore=self.__KVSTORE, scope=self.__rfid)
        cache = {}
        for kvobj in kvstore:
            cache[kvobj.key] = kvobj.value
        return cache


    def __pypolestar_dumper(self, cache):
        if self.__rfid is None:
            self.__logger.error('__pypolestar_dumper - No rfid id as scope object to write cache with!')

        stored_cache = self.__pypolestar_loader()
        # Generate diff
        to_delete = list(set(stored_cache) - set(cache))
        to_add = list(set(cache) - set(stored_cache))
        to_update = list(set(cache) & set(stored_cache))

        # Run through to-delete keys
        for email in to_delete:
            self.__logger.info('__pypolestar_dumper - delete kvstore={} scope={} email={}'.format(self.__KVSTORE, self.__rfid, email))
            kvs = KeyValueStoreModel.get_value(kvstore=self.__KVSTORE, scope=self.__rfid, key=email)
            kvs.delete()

        # Run through to-add keys
        for email in to_add:
            self.__logger.info('__pypolestar_dumper - add kvstore={} scope={} email={}'.format(self.__KVSTORE, self.__rfid, email))
            kvs = KeyValueStoreModel(kvstore=self.__KVSTORE, scope=self.__rfid, key=email, value=cache[email])
            kvs.save()

        # Run through to-update keys
        for email in to_update:
            self.__logger.info('__pypolestar_dumper - update kvstore={} scope={} email={}'.format(self.__KVSTORE, self.__rfid, email))
            kvs = KeyValueStoreModel.get_value(kvstore=self.__KVSTORE, scope=self.__rfid, key=email)
            kvs.value=cache[email]
            kvs.save()

    def __pypolestar_update_cache_entry(self, username:str=None, polestarAuth:PolestarAuth=None):
        # Update the cache entry with new tokens
        cache = self.__pypolestar_loader()
        entry = {}
        entry['username'] = polestarAuth.username
        entry['access_token'] = polestarAuth.access_token
        entry['token_expiry'] = polestarAuth.token_expiry.isoformat()
        # entry['token_expiry'] = polestarAuth.token_expiry
        # entry['token_lifetime'] = str(polestarAuth.token_lifetime)
        entry['token_lifetime'] = polestarAuth.token_lifetime
        entry['refresh_token'] = polestarAuth.refresh_token
        # cache[username] = json.dumps(entry)
        cache[username] = entry
        self.__pypolestar_dumper(cache=cache)

    def __pypolestar_delete_cache_entry(self, username:str=None):
        # Load from cache
        cache = self.__pypolestar_loader()
        if username not in cache:
            self.__logger.warning("__pypolestar_delete_cache_entry() - No cached session for username {}.".format(username))
            return
        # Remove entry
        del cache[username]
        self.__pypolestar_dumper(cache=cache)

    def __pypolestar_use_cache_entry(self, username:str=None, polestarAuth:PolestarAuth=None):
        # Load from cache
        cache = self.__pypolestar_loader()
        if username not in cache:
            self.__logger.warning("__pypolestar_use_cache_entry() - No cached session for username {}.".format(username))
            return
        # entry = json.loads( cache[username] )
        entry = cache[username]
        # Update the api with the cached tokens
        polestarAuth.username = entry['username'] 
        polestarAuth.access_token = entry['access_token'] 
        polestarAuth.token_expiry = datetime.fromisoformat( entry['token_expiry'] )
        polestarAuth.token_lifetime = int( entry['token_lifetime'] )
        polestarAuth.refresh_token = entry['refresh_token'] 


    def authorizeByUsernamePassword(self, username:str=None, password:str=None) -> bool:
        if username is None:
            username = self.__username
        if username is None:
            self.__logger.warning("authorizeByUsernamePassword() - Cannot authorize - no username.")
            return False
        if password is None:
            self.__logger.warn("authorizeByUsernamePassword() - Cannot authorize - no password.")
            return False
        # Establish account
        self.__api = PolestarApi(username=username, password=password)

        # Initialize (login / setup)
        try:
            asyncio.run(self.__api.async_init())
        except Exception as e:
            self.__logger.warning('authorizeByUsernamePassword - Authentication failed! {}'.format(str(e)))
            return False

        # Update the kvstore with new tokens
        self.__pypolestar_update_cache_entry(username=username, polestarAuth=self.__api.auth)

        return True

    """
        TODO: The username here is not used, the refresh token gives all access. The username used to gain access is
        stored in the cache for pypolestar, so we could check for it.
    """
    def authorizeByRefreshToken(self, username:str=None, refresh_token:str=None, rfid:str=None) -> bool:
        if username is None:
            username = self.__username
        if username is None:
            self.__logger.warning("authorizeByRefreshToken() - Cannot authorize - no username.")
            return False
        if rfid is not None:
            self.__rfid = rfid
        if self.__rfid is None:
            self.__logger.warning("authorizeByRefreshToken() - Cannot authorize - no rfid.")
            return False
        # Establish account

        # API client - no user account
        self.__api = PolestarApi(username=None, password=None)
        # Inject refgresh token
        self.__api.auth.refresh_token = refresh_token

        # Re-establish the session from existing tokens (login / setup)
        try:
            asyncio.run(self.__api.async_init())
        except Exception as e:
            # Invalid refresh token
            self.__logger.warning("authorizeByRefreshToken() - autorisation failed.")
            return False
        
        # Update the kvstore with new tokens
        self.__pypolestar_update_cache_entry(username=username, polestarAuth=self.__api.auth)

        return True


    def isAuthorized(self, username:str=None) -> bool:

        if username is None:
            username = self.__username
        if username is None:
            self.__logger.warning("isAuthorized() - Cannot identify authorization status, no user information.")
            return False
        if self.__api is None:
            # Load from cache
            self.__api = PolestarApi(username=username, password=None)
            self.__pypolestar_use_cache_entry(username=username, polestarAuth=self.__api.auth)
            if self.__api is None:
                self.__logger.warning("isAuthorized() - Cannot identify authorization status, no user or session information.")
                return False
            
        # Initialize (login / setup)
        try:
            asyncio.run(self.__api.async_init())
        except Exception as e:
            self.__logger.warning("isAuthorized() - authorisation failed.")
            self.__api = None
            # Remove the invalid cache entry
            self.__pypolestar_delete_cache_entry(username=username)
            return False
        
        # Update the kvstore with new tokens
        self.__pypolestar_update_cache_entry(username=self.__api.auth.username, polestarAuth=self.__api.auth)

        return True


    """
        Does not wake up vehicle
    """
    def getVehicleList(self, username:str=None, max_retries:int=3):
        if username is None:
            username = self.__username
        if username is None:
            self.__logger.warning("getVehicleList() - Cannot get vehicle list for username {}.".format(username))
            return []

        if not self.isAuthorized(username=username):
            self.__logger.warning("getVehicleList() - Cannot get vehicle list for username {}. Not autorized.".format(username))
            return []

        vehicles = []
        try:
            vins = self.__api.get_available_vins()

            # Update the kvstore with new tokens
            self.__pypolestar_update_cache_entry(username=self.__api.auth.username, polestarAuth=self.__api.auth)

            for vin in vins:
                info = self.__api.get_car_information(vin=vin)
                vehicle = {}
                vehicle["vin"] = vin
                vehicle["model_name"] = info.model_name
                vehicle["registration_date"] = info.registration_date.strftime("%d-%m-%Y")
                vehicle["registration_no"] = info.registration_no
                vehicles.append(vehicle)
            return vehicles
        except Exception as e:
            self.__logger.warning("getVehicleList() - Cannot get vehicle list for username {}. {}".format(username, str(e)))
            return []

    """
        Grab specific information from the vehicle data, in this case the odometer value
    """
    def getOdometer(self, username:str=None, vin:str=None, max_retries:int=3, odoInKm:bool=True) -> int:
        if username is None:
            username = self.__username
        if username is None:
            self.__logger.warning("getOdometer() - Cannot get vehicle data for username {}.".format(username))
            return None

        if not self.isAuthorized(username=username):
            self.__logger.warning("getOdometer() - Cannot get vehicle data for username {}. Not autorized.".format(username))
            return None

        try:
            # Update latest data (telematics: battery, odometer etc.)
            asyncio.run(self.__api.update_latest_data(vin=vin, update_telematics=True))
            # Update the kvstore with new tokens
            self.__pypolestar_update_cache_entry(username=self.__api.auth.username, polestarAuth=self.__api.auth)

            info = self.__api.get_car_telematics(vin=vin)
            odometerInMeters = info.odometer.odometer_meters
            odometerInKm = round( odometerInMeters / 1000 )
            odometerInMiles = round( odometerInMeters / 1000 * 0.621371 )
            self.__logger.debug("getOdometer() - odometer: {}M or {}km".format(odometerInMiles, odometerInKm))

            return odometerInKm if odoInKm else odometerInMiles
        except Exception as e:
            self.__logger.warning("getOdometer() - Cannot get vehicle data for username {}. {}".format(username, str(e)))
            return None
        
    """
        Logout clears the token
    """
    def logout(self, username:str=None):
        if username is None:
            username = self.__username
        if username is None:
            self.__logger.warning("logout() - Cannot get vehicle data for username {}.".format(username))
            return None

        # Find and establish the session
        self.isAuthorized(username=username)

        if self.__api is None:
            self.__logger.warning("logout() - Cannot logout for username {}. No active session.".format(username))
            return True
        
        """Log out from Polestar API."""
        asyncio.run(self.__api.async_logout())

        # Clean from cache
        self.__pypolestar_delete_cache_entry(username=username)

        return True

