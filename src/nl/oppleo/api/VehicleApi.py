import logging
from weakref import ref
from nl.oppleo.models.RfidModel import RfidModel

from nl.oppleo.api.tesla.TeslaPyWrapper import TeslaPyWrapper
from nl.oppleo.api.tesla.TeslaApiFormatters import formatTeslaVehicle, formatTeslaChargeState

from nl.oppleo.api.polestar.PolestarPyWrapper import PolestarPyWrapper

"""
    Generic vehicle interface for Oppleo
    
    implementations for:
    - Tesla
    - Polestar (dec 2025)

    authorizeByRefreshToken
    getAuthorizationUrl - Tesla specific
    authorizeByUrl - Tesla specific
    isAuthorized
    getVehicleList
    isAvailable
    getVehicleData - return is Tesla/Polestar specific
    getOdometer
    getChargeState
    composeImage - Tesla specific
    logout

"""

class VehicleApi:
    __logger = None
    __rfid_model = None

    def __init__(self, rfid_model:RfidModel=None):
        self.__logger = logging.getLogger(self.__class__.__module__)
        self.__logger.debug('VehicleApi.__init__')
        self.__rfid_model=rfid_model


    def authorizeByUsernamePassword(self, rfid_model:RfidModel=None, vehicle_make:str=None, username:str=None, password:str=None):
        if rfid_model is None:
            rfid_model = self.__rfid_model
        if rfid_model is None:
            self.__logger.warning("authorizeByUsernamePassword() - Cannot authorize for rfid_model")
            return

        if vehicle_make == "Tesla":
            # Not working at htis moment!
            self.__logger.error("authorizeByUsernamePassword() - Not supported for Tesla")
            return

        if vehicle_make == "Polestar":
            # Establish account
            ppw = PolestarPyWrapper(rfid=rfid_model.rfid, username=username)
            return ppw.authorizeByUsernamePassword(username=username, password=password)

        self.__logger.warning("authorizeByUsernamePassword() - Cannot authorize for unsupported vehicle make ({})".format(rfid_model.vehicle_make))
        return


    def authorizeByRefreshToken(self, rfid_model:RfidModel=None, account:str=None, refresh_token:str=None, vehicle_make:str=None, rfid:str=None):
        if account is None:
            account = rfid_model.api_account if rfid_model is not None else ( self.__rfid_model.api_account if self.__rfid_model is not None else None )
        if account is None:
            self.__logger.warning("authorizeByRefreshToken() - Cannot authorize for rfid_model/account.")
            return

        if rfid is None:
            rfid = rfid_model.rfid if rfid_model is not None else ( self.__rfid_model.rfid if self.__rfid_model is not None else None )
        if rfid is None:
            self.__logger.warning("authorizeByRefreshToken() - Cannot authorize for rfid.")
            return

        if vehicle_make is None:
            vehicle_make = rfid_model.vehicle_make if rfid_model is not None else ( self.__rfid_model.vehicle_make if self.__rfid_model is not None else None )
        if vehicle_make is None:
            self.__logger.warning("getAuthorizationUrl() - Cannot authorize rfid_model/account - no vehicle make.")
            return

        if vehicle_make == "Tesla":
            # Establish account
            tpw = TeslaPyWrapper(email=account)
            return tpw.authorizeByRefreshToken(refresh_token=refresh_token, rfid=rfid)

        if vehicle_make == "Polestar":
            # Establish account
            ppw = PolestarPyWrapper(username=account)
            return ppw.authorizeByRefreshToken(refresh_token=refresh_token, rfid=rfid)
        
        self.__logger.warning("authorizeByRefreshToken() - Cannot authorize for unsupported vehicle make ({})".format(rfid_model.vehicle_make))


    def getAuthorizationUrl(self, rfid_model:RfidModel=None, account:str=None, vehicle_make:str=None) -> str:
        if account is None:
            account = rfid_model.api_account if rfid_model is not None else ( self.__rfid_model.api_account if self.__rfid_model is not None else None )
        if account is None:
            self.__logger.warning("getAuthorizationUrl() - Cannot create url for rfid_model/account.")
            return None

        if vehicle_make is None:
            vehicle_make = rfid_model.vehicle_make if rfid_model is not None else ( self.__rfid_model.vehicle_make if self.__rfid_model is not None else None )
        if vehicle_make is None:
            self.__logger.warning("getAuthorizationUrl() - Cannot authorize rfid_model/account - no vehicle make.")
            return

        if vehicle_make == "Tesla":
            # Establish account
            tpw = TeslaPyWrapper(email=account)
            return tpw.getAuthorizationUrl()

        self.__logger.warning("getAuthorizationUrl() - Cannot get authorization url for unsupported vehicle make ({})".format(rfid_model.vehicle_make))
        return None


    def authorizeByUrl(self, rfid_model:RfidModel=None, account:str=None, url:str=None, vehicle_make:str=None, rfid:str=None) -> bool:
        if account is None:
            account = rfid_model.api_account if rfid_model is not None else ( self.__rfid_model.api_account if self.__rfid_model is not None else None )
        if account is None:
            self.__logger.warning("authorizeByRefreshToken() - Cannot authorize rfid_model/account - no account.")
            return False

        if rfid is None:
            rfid = rfid_model.rfid if rfid_model is not None else ( self.__rfid_model.rfid if self.__rfid_model is not None else None )
        if rfid is None:
            self.__logger.warning("authorizeByRefreshToken() - Cannot authorize for rfid.")
            return False

        if vehicle_make is None:
            vehicle_make = rfid_model.vehicle_make if rfid_model is not None else ( self.__rfid_model.vehicle_make if self.__rfid_model is not None else None )
        if vehicle_make is None:
            self.__logger.warning("authorizeByRefreshToken() - Cannot authorize rfid_model/account - no vehicle make.")
            return False

        if vehicle_make == "Tesla":
            # Establish account
            tpw = TeslaPyWrapper(email=account)
            return tpw.authorizeByUrl(url=url, rfid=rfid)

        self.__logger.warning("authorizeByUrl() - Cannot get authorizate by url for unsupported vehicle make ({})".format(rfid_model.vehicle_make))
        return False

    """
        Expected: an authorization is expected. If not, no warning logged (just querying)
    """
    def isAuthorized(self, rfid_model:RfidModel=None, expected:bool=True) -> bool:
        if rfid_model is None:
            rfid_model = self.__rfid_model
        if rfid_model is None or rfid_model.api_account is None:
            # No authorization, expected?
            if expected:
                # Log as warning
                self.__logger.warning("isAuthorized() - Cannot identify authorization status for rfid_model (rfid={}, name={}).".format(
                        "None" if rfid_model is None else rfid_model.rfid, 
                        "None" if rfid_model is None else rfid_model.name)
                        )
                # Potentially log a trace
                # import inspect, traceback
                # frame = inspect.currentframe()
                # stack_trace = traceback.format_stack(frame)
                # self.__logger.warning(stack_trace[:-1])

            return False

        if rfid_model.vehicle_make == "Tesla":
            # Establish account
            tpw = TeslaPyWrapper(email=rfid_model.api_account, rfid=rfid_model.rfid)
            if not tpw.isAuthorized(email=rfid_model.api_account):
                tpw.teslaLogout()
            return tpw.isAuthorized(email=rfid_model.api_account)

        if rfid_model.vehicle_make == "Polestar":
            # Establish account
            ppw = PolestarPyWrapper(username=rfid_model.api_account, rfid=rfid_model.rfid)
            return ppw.isAuthorized(username=rfid_model.api_account)

        self.__logger.warning("isAuthorized() - Cannot get authorizate by url for unsupported vehicle make ({})".format(rfid_model.vehicle_make))
        return False


    def getVehicleList(self, rfid_model:RfidModel=None, max_retries:int=3):
        if rfid_model is None:
            rfid_model = self.__rfid_model
        if rfid_model is None or rfid_model.api_account is None:
            self.__logger.warning("getVehicleList() - Cannot get vehicle list for rfid_model.")
            return []

        if rfid_model.vehicle_make == "Tesla":
            # Establish account
            tpw = TeslaPyWrapper(email=rfid_model.api_account, rfid=rfid_model.rfid)
            return tpw.getVehicleList(max_retries=max_retries)

        if rfid_model.vehicle_make == "Polestar":
            # Establish account
            ppw = PolestarPyWrapper(username=rfid_model.api_account, rfid=rfid_model.rfid)
            return ppw.getVehicleList(max_retries=max_retries)

        self.__logger.warning("getVehicleList() - Cannot get vehicle list for unsupported vehicle make ({})".format(rfid_model.vehicle_make))
        return []


    """
        Does not wake up vehicle
    """
    def isAvailable(self, rfid_model:RfidModel=None) -> bool:
        if rfid_model is None:
            rfid_model = self.__rfid_model
        if rfid_model is None or rfid_model.api_account is None:
            self.__logger.warning("isAvailable() - Cannot get vehicle wake state for rfid_model.")
            return False

        if rfid_model.vehicle_make == "Tesla":
            # Establish account
            tpw = TeslaPyWrapper(email=rfid_model.api_account, rfid=rfid_model.rfid)
            return tpw.isAvailable(vin=rfid_model.vehicle_vin)

        self.__logger.warning("isAvailable() - Cannot get vehicle wake state for unsupported vehicle make ({})".format(rfid_model.vehicle_make))
        return False


    def getVehicleData(self, rfid_model:RfidModel=None, max_retries:int=3, wake_up:bool=False) -> dict:
        if rfid_model is None:
            rfid_model = self.__rfid_model
        if rfid_model is None or rfid_model.api_account is None:
            self.__logger.warning("getVehicleData() - Cannot get vehicle data for rfid_model.")
            return None

        if rfid_model.vehicle_make == "Tesla":
            # Establish account
            tpw = TeslaPyWrapper(email=rfid_model.api_account, rfid=rfid_model.rfid)
            if not wake_up and not tpw.isAvailable(vin=rfid_model.vehicle_vin):
                return formatTeslaVehicle(
                                tpw.getVehicle(vin=rfid_model.vehicle_vin)
                            )
            return formatTeslaVehicle(
                            tpw.getVehicleData(vin=rfid_model.vehicle_vin, max_retries=max_retries, wake_up=wake_up)
                        )

        self.__logger.warning("getVehicleData() - Cannot get vehicle data for unsupported vehicle make ({})".format(rfid_model.vehicle_make))
        return None


    """
        Grab specific information from the vehicle data, in this case the odometer value
    """

    def getOdometer(self, rfid_model:RfidModel=None, max_retries:int=3, wake_up:bool=True, odoInKm:bool=True) -> int:
        if rfid_model is None:
            rfid_model = self.__rfid_model
        if rfid_model is None or rfid_model.api_account is None:
            self.__logger.warning("getOdometer() - Cannot get odometer for rfid_model.")
            return None

        if rfid_model.vehicle_make == "Tesla":
            # Establish account
            tpw = TeslaPyWrapper(email=rfid_model.api_account, rfid=rfid_model.rfid)
            return tpw.getOdometer(vin=rfid_model.vehicle_vin, max_retries=max_retries, wake_up=wake_up )

        if rfid_model.vehicle_make == "Polestar":
            # Establish account
            ppw = PolestarPyWrapper(username=rfid_model.api_account, rfid=rfid_model.rfid)
            return ppw.getOdometer(vin=rfid_model.vehicle_vin, max_retries=max_retries )

        self.__logger.warning("getOdometer() - Cannot get vehicle data for unsupported vehicle make ({})".format(rfid_model.vehicle_make))
        return None


    def getChargeState(self, rfid_model:RfidModel=None, max_retries:int=3, wake_up:bool=False) -> dict:

        # TODO - temp
        self.__logger.error("getChargeState() !!!!! wake_up: {}".format(wake_up))


        if rfid_model is None:
            rfid_model = self.__rfid_model
        if rfid_model is None or rfid_model.api_account is None:
            self.__logger.warning("getChargeState() - Cannot get vehicle charge state for rfid_model.")
            return None

        if rfid_model.vehicle_make == "Tesla":
            # Establish account
            tpw = TeslaPyWrapper(email=rfid_model.api_account, rfid=rfid_model.rfid)
            return formatTeslaChargeState(
                            tpw.getChargeState(vin=rfid_model.vehicle_vin, max_retries=max_retries, wake_up=wake_up)
                        )   

        self.__logger.warning("getChargeState() - Cannot get vehicle charge state for unsupported vehicle make ({})".format(rfid_model.vehicle_make))
        return None


    """
        Returns a PNG formatted composed vehicle image. Valid views are:
          STUD_3QTR, STUD_SEAT, STUD_SIDE, STUD_REAR and STUD_WHEEL
    """
    def composeImage(self, rfid_model:RfidModel=None, account:str=None, vehicle_make:str=None, vin:str=None, view:str='STUD_3QTR'):
        if rfid_model is None:
            rfid_model = self.__rfid_model
        if rfid_model is None or rfid_model.api_account is None:
            self.__logger.warning("composeImage() - Cannot compose vehicle image for rfid_model.")
            return None

        if account is None:
            account = rfid_model.api_account if rfid_model is not None else ( self.__rfid_model.api_account if self.__rfid_model is not None else None )
        if account is None:
            self.__logger.warning("composeImage() - Cannot compose vehicle image - no account.")
            return None

        if vin is None:
            vin = rfid_model.vehicle_vin if rfid_model is not None else ( self.__rfid_model.vehicle_vin if self.__rfid_model is not None else None )
        if vin is None:
            self.__logger.warning("composeImage() - Cannot compose vehicle image - vin.")
            return None

        if vehicle_make is None:
            vehicle_make = rfid_model.vehicle_make if rfid_model is not None else ( self.__rfid_model.vehicle_make if self.__rfid_model is not None else None )
        if vehicle_make is None:
            self.__logger.warning("composeImage() - Cannot compose vehicle image - no vehicle make.")
            return None

        if vehicle_make == "Tesla":
            # Establish account
            tpw = TeslaPyWrapper(email=rfid_model.api_account, rfid=rfid_model.rfid)
            return tpw.composeImage(vin=vin, view=view)
        
        # TODO: Image generation for Polestar

        self.__logger.warning("composeImage() - Cannot logout for unsupported vehicle make ({})".format(rfid_model.vehicle_make))
        return None


    """
        Logout clears the token
    """
    def logout(self, rfid_model:RfidModel=None, account:str=None, vehicle_make:str=None):
        if account is None:
            account = rfid_model.api_account if rfid_model is not None else ( self.__rfid_model.api_account if self.__rfid_model is not None else None )
        if account is None:
            self.__logger.warning("logout() - Cannot logout rfid_model/account - no account.")
            return False

        if vehicle_make is None:
            vehicle_make = rfid_model.vehicle_make if rfid_model is not None else ( self.__rfid_model.vehicle_make if self.__rfid_model is not None else None )
        if vehicle_make is None:
            self.__logger.warning("logout() - Cannot logout rfid_model/account - no vehicle make.")
            return None

        if vehicle_make == "Tesla":
            # Establish account
            tpw = TeslaPyWrapper(email=account)
            return tpw.logout()

        if vehicle_make == "Polestar":
            # Establish account
            ppw = PolestarPyWrapper(username=account)
            return ppw.logout()

        self.__logger.warning("logout() - Cannot logout for unsupported vehicle make ({})".format(rfid_model.vehicle_make))
        return None

