import logging
import threading
import datetime
from flask_socketio import SocketIO

from nl.oppleo.config.OppleoConfig import OppleoConfig

from nl.oppleo.api.TeslaApi import TeslaAPI
from nl.oppleo.models.ChargeSessionModel import ChargeSessionModel
from nl.oppleo.models.RfidModel import RfidModel

from nl.oppleo.utils.TokenMediator import tokenMediator

from nl.oppleo.services.PushMessage import PushMessage

oppleoConfig = OppleoConfig()

"""
 Instantiate object
 Set the session id
 call start on it
"""


class UpdateOdometerTeslaUtil:
    __logger = None
    charge_session_id = None
    thread = None
    threadLock = None
    condense = False


    def __init__(self):
        self.__logger = logging.getLogger('nl.oppleo.utils.UpdateOdometerTeslaUtil')
        self.__logger.debug('UpdateOdometerTeslaUtil.__init__')
        self.thread = None
        self.threadLock = threading.Lock()


    def set_charge_session_id(self, charge_session_id=None):
        self.charge_session_id = charge_session_id


    def set_condense(self, condense=False):
        self.condense = condense


    def start(self):
        self.__logger.debug(f'{datetime.datetime.now()} - Launching background task...')
        self.thread = oppleoConfig.appSocketIO.start_background_task(self.update_odometer)


    def update_odometer(self):
        self.__logger.debug("update_odometer()")
        # This method starts a thread which grabs the odometer value and updates the session table
        if self.charge_session_id is None:
            self.__logger.debug("update_odometer() - No session id")
            return
        charge_session = ChargeSessionModel.get_one_charge_session(self.charge_session_id)
        if charge_session is None:
            self.__logger.debug("update_odometer() - Session with id {} not found.".format(self.charge_session_id))
            return
        rfid_model = RfidModel.get_one(charge_session.rfid)
        if rfid_model is None:
            self.__logger.debug("update_odometer() - Rfid {} not found.".format(charge_session.rfid))
            return
        if rfid_model.api_access_token is None:
            self.__logger.debug("update_odometer() - API Access token for Rfid {} not found.".format(charge_session.rfid))
            return
        # Valid token?
        t_api = TeslaAPI()

        # Token, checkout
        tKey = tokenMediator.checkout(token=rfid_model.api_access_token, ref='UpdateOdometerTeslaUtil: '+rfid_model.rfid, wait=True)
        if tKey is None:
            # Checkout failed? Token must not be valid anymore
            if not tokenMediator.validate(token=rfid_model.api_access_token):
                self.__logger.debug("update_odometer() token not valid, done here for now")
            else:
                self.__logger.warn("update_odometer() checkout failed, not sure what went wrong")
            return

        UpdateOdometerTeslaUtil.copy_token_from_rfid_model_to_api(rfid_model=rfid_model, tesla_api=t_api)
        if not t_api.hasValidToken():
            self.__logger.debug("update_odometer() - Token has expired.")
            # Not valid, invalidate and return
            tokenMediator.invalidate(token=rfid_model.api_access_token, key=tKey, ref='UpdateOdometerTeslaUtil: '+rfid_model.rfid)
            # Notify through push messages if configured
            PushMessage.sendMessage(
                "Tesla token expired", 
                "The Tesla OAuth token for rfid {} ({}) has expired."
                .format(
                    rfid_model.name,
                    rfid_model.rfid
                    )
                )
            return

        # Refresh if required
        if t_api.refreshTokenIfRequired():
            # Invalidate the old token
            tokenMediator.invalidate(token=rfid_model.api_access_token, key=tKey, ref='UpdateOdometerTeslaUtil: '+rfid_model.rfid)
            UpdateOdometerTeslaUtil.copy_token_from_api_to_rfid_model(t_api, rfid_model)
            # Checkout the new token
            tKey = tokenMediator.checkout(token=rfid_model.api_access_token, ref='UpdateOdometerTeslaUtil: '+rfid_model.rfid, wait=True)
            rfid_model.save()

        # get the odometer
        odometer = t_api.getOdometerWithId(rfid_model.vehicle_id)

       # Did the token still work?
        if t_api.got401Unauthorized:
            # Nah, report
            self.__logger.warn('Token led to 401 Unauthorized. Removing token')
            tokenMediator.invalidate(token=rfid_model.api_access_token, key=tKey, ref='UpdateOdometerTeslaUtil: '+rfid_model.rfid)
            rfid_model.clean_token_rfid_model()
            rfid_model.get_odometer = False
            # Inform through push messages if configured
            PushMessage.sendMessage(
                "Tesla token invalid", 
                "Encountered 401 Unauthorized when updating odometer for charge session {}." + \
                    " Removing token from rfid tag {} ({})."
                .format(
                    self.charge_session_id,
                    rfid_model.name,
                    rfid_model.rfid
                    )
                )

        # Release the token
        tokenMediator.release(token=rfid_model.api_access_token, key=tKey)

        with self.threadLock:
            charge_session = ChargeSessionModel.get_one_charge_session(self.charge_session_id)
            if charge_session is None:
                self.__logger.error("Charge session with id {} could no longer be found. (Condensed?)".format(self.charge_session_id))
                # Inform through push messages if configured
                PushMessage.sendMessage(
                    "Charge session not found", 
                    "Charge session with id {} could no longer be found, when adding odometer value. (Condensed?)."
                    .format(
                        self.charge_session_id
                        )
                    )
                return
            charge_session.km = odometer
            charge_session.save()
        self.__logger.debug("Obtained odometer {} for {} ".format(
            charge_session.km,
            rfid_model.vehicle_name
        ))
        """
        CONDENSE
            - if condense was requested (only for auto-generated sessions with odometer value)
            - Find a previous charge session, on the same charge point, with the same odometer value, 
              with an end_value equal to the start_value of the new session (correct sequence)
            - Don't condense if the odometer value could not be obtained, or if the charge session was 
              not AUTO started (but by human RFID tag or from WEB interface, only condense AUTO sessions)
              The previous session to condense with could be started by any way.
        """ 
        self.__logger.debug("Check condense... (condense = {}, odometer = {}, ChargeSession.trigger = {} "
                    .format(
                        self.condense,
                        odometer,
                        charge_session.trigger
                    ))
        if self.condense and \
           odometer is not None and \
           charge_session.trigger == ChargeSessionModel.TRIGGER_AUTO:
            with self.threadLock:
                # charge_session is the new charge session, was there a previous charge session just like this one?
                same_charge_session = ChargeSessionModel.get_specific_charge_session(
                                                energy_device_id=charge_session.energy_device_id, 
                                                rfid=charge_session.rfid, 
                                                km=charge_session.km, 
                                                end_value=charge_session.end_value, 
                                                tariff=charge_session.tariff
                                                )
                if same_charge_session != None:
                    self.__logger.debug("same_charge_session found! Condense...")
                    condenseSucceeded = ChargeSessionModel.condense_charge_sessions(
                                            closed_charge_session=same_charge_session,
                                            new_charge_session=charge_session
                                            )
 


    @staticmethod
    def copy_token_from_rfid_model_to_api(rfid_model, tesla_api):
        tesla_api.access_token = rfid_model.api_access_token
        tesla_api.token_type = rfid_model.api_token_type
        tesla_api.created_at = rfid_model.api_created_at
        tesla_api.expires_in = rfid_model.api_expires_in
        tesla_api.refresh_token = rfid_model.api_refresh_token

    @staticmethod
    def copy_token_from_api_to_rfid_model(tesla_api, rfid_model):
        rfid_model.api_access_token = tesla_api.access_token
        rfid_model.api_token_type = tesla_api.token_type
        rfid_model.api_created_at = tesla_api.created_at
        rfid_model.api_expires_in = tesla_api.expires_in
        rfid_model.api_refresh_token = tesla_api.refresh_token

    @staticmethod
    def clean_token_rfid_model(rfid_model):
        rfid_model.api_access_token = None
        rfid_model.api_token_type = None
        rfid_model.api_created_at = None
        rfid_model.api_expires_in = None
        rfid_model.api_refresh_token = None
