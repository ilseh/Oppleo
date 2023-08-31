import logging
from nl.oppleo import config
import threading
import datetime
from flask_socketio import SocketIO

from nl.oppleo.config.OppleoConfig import OppleoConfig
from nl.oppleo.utils.OutboundEvent import OutboundEvent

from nl.oppleo.models.ChargeSessionModel import ChargeSessionModel
from nl.oppleo.models.RfidModel import RfidModel

# from nl.oppleo.utils.TokenMediator import tokenMediator
from nl.oppleo.api.VehicleApi import VehicleApi

from nl.oppleo.services.PushMessage import PushMessage

oppleoConfig = OppleoConfig()

"""
 Instantiate object
 Set the session id
 call start on it
"""


class UpdateOdometerTeslaUtil:
    __logger = None
    __charge_session_id = None
    __thread = None
    __threadLock = None
    __condense = False


    def __init__(self):
        self.__logger = logging.getLogger('nl.oppleo.utils.UpdateOdometerTeslaUtil')
        self.__logger.debug('UpdateOdometerTeslaUtil.__init__')
        self.__thread = None
        self.__threadLock = threading.Lock()

    @property
    def charge_session_id(self):
        return self.__charge_session_id

    @charge_session_id.setter
    def charge_session_id(self, value):
        with self.__threadLock:
            self.__charge_session_id = value

    @property
    def condense(self):
        return self.__condense

    @condense.setter
    def condense(self, value):
        with self.__threadLock:
            self.__condense = value


    def start(self):
        self.__logger.debug(f'{datetime.datetime.now()} - Launching background task...')
        self.__thread = oppleoConfig.appSocketIO.start_background_task(self.update_odometer)


    def sendChargeSessionUpdate(self, event:str=None, data:str=None, namespace:str='/charge_session', public:bool=False):
        self.__logger.debug('sendChargeSessionUpdate() - event:{}, data:{}'.format(event, data))
        if event is None or data is None:
            return
        OutboundEvent.triggerEvent(
                event=event,
                id=oppleoConfig.chargerID,
                data=data,
                namespace='/charge_session',
                public=public
            )            



    def update_odometer(self):
        self.__logger.debug("update_odometer()")
        self.sendChargeSessionUpdate(event='odomoter_update_started', data={ 'status': True, 'chargeSessionId': self.charge_session_id })

        # This method starts a thread which grabs the odometer value and updates the session table
        if self.__charge_session_id is None:
            self.__logger.debug("update_odometer() - No session id")
            self.sendChargeSessionUpdate(event='odomoter_update_ended', data={ 'status': False, 'chargeSessionId': self.charge_session_id, 'code': 481, 'reason': 'No session id' })
            return
        charge_session = ChargeSessionModel.get_one_charge_session(self.__charge_session_id)
        if charge_session is None:
            self.__logger.debug("update_odometer() - Session with id {} not found.".format(self.__charge_session_id))
            self.sendChargeSessionUpdate(event='odomoter_update_ended', data={ 'status': False, 'chargeSessionId': self.charge_session_id, 'code': 482, 'reason': 'No session' })
            return
        rfid_model = RfidModel.get_one(charge_session.rfid)
        if rfid_model is None:
            self.__logger.debug("update_odometer() - Rfid {} not found.".format(charge_session.rfid))
            self.sendChargeSessionUpdate(event='odomoter_update_ended', data={ 'status': False, 'chargeSessionId': self.charge_session_id, 'code': 483, 'reason': 'No rfid token' })
            return

        vApi = VehicleApi(rfid_model=rfid_model)

        """ BUGFIX 
            Sometimes the odometer is not obtained. Try again up to 3 times. let's see if that makes the issue go away
            TODO: make retries configurable. Make delay between tries configurable
        """
        retries = 0
        odometer = None
        while retries < 3 and odometer == None:
            odometer = vApi.getOdometer(odoInKm=True)
            if odometer == None:
                retries = retries +1
                self.__logger.error("ODOMETER NOT OBTAINED - try # {} of 3...".format(retries))

        # Did the token still work?
        if not vApi.isAuthorized():
            # Nah, report
            self.__logger.warn('Token not authorizing. Removing authorization (token)')
            vApi.logout()

            rfid_model.cleanupVehicleInfo()
            
            # Inform through push messages if configured
            PushMessage.sendMessage(
                "Tesla token invalid", 
                "Unauthorized when updating odometer for charge session {}." + \
                    " Removing token from rfid tag {} ({})."
                .format(
                    self.__charge_session_id,
                    rfid_model.name,
                    rfid_model.rfid
                    )
                )

        if odometer is None:
            self.__logger.debug("Odometer not retrieved for {} with rfid {} ({}) on charge session {} ".format(
                rfid_model.vehicle_name,
                rfid_model.name,
                rfid_model.rfid,
                self.__charge_session_id
            ))
            PushMessage.sendMessage(
                "Tesla odometer update failed", 
                "Could not retrieve odometer value for rfid {} ({}) on charge session {}."
                .format(
                    rfid_model.name,
                    rfid_model.rfid,
                    self.__charge_session_id
                    )
                )
            self.sendChargeSessionUpdate(event='odomoter_update_ended', data={ 'status': False, 'chargeSessionId': self.charge_session_id, 'code': 486, 'reason': 'No odometer value' })
            return

        with self.__threadLock:
            charge_session = ChargeSessionModel.get_one_charge_session(self.__charge_session_id)
            if charge_session is None:
                self.__logger.error("Charge session with id {} could no longer be found. (Condensed?)".format(self.__charge_session_id))
                # Inform through push messages if configured
                PushMessage.sendMessage(
                    "Charge session not found", 
                    "Charge session with id {} could no longer be found, when adding odometer value. (Condensed?)."
                    .format(
                        self.__charge_session_id
                        )
                    )
                self.sendChargeSessionUpdate(event='odomoter_update_ended', data={ 'status': False, 'chargeSessionId': self.charge_session_id, 'code': 487, 'reason': 'No charge session' })
                return
            charge_session.km = odometer
            charge_session.save()
        self.__logger.debug("Obtained odometer {} for {} ".format(
            charge_session.km,
            rfid_model.vehicle_name
        ))

        self.sendChargeSessionUpdate(event='odomoter_update_ended', data={ 'status': True, 'chargeSessionId': self.charge_session_id })
        self.sendChargeSessionUpdate(event='charge_session_data_update', data=charge_session.to_str())

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
                        self.__condense,
                        odometer,
                        charge_session.trigger
                    ))
        if ( self.__condense and
             odometer is not None and
             charge_session.trigger == ChargeSessionModel.TRIGGER_AUTO
           ):
            with self.__threadLock:
                # TODO - keep condensing, get_specific_closed_charge_session order by highest number
                # charge_session is the new charge session, was there a previous charge session just like this one?
                same_charge_session = ChargeSessionModel.get_specific_closed_charge_session(
                                                energy_device_id=charge_session.energy_device_id, 
                                                rfid=charge_session.rfid, 
                                                km=charge_session.km, 
                                                end_value=charge_session.start_value, 
                                                tariff=charge_session.tariff
                                                )
                if same_charge_session != None:
                    self.__logger.debug("same_charge_session found ({})! Condense...".format(same_charge_session.id))
                    # Save the id, get's lost if condensed
                    same_charge_session_id = same_charge_session.id
                    ChargeSessionModel.condense_charge_sessions(
                        closed_charge_session=same_charge_session,
                        new_charge_session=charge_session
                        )
                    if (len(oppleoConfig.connectedClients) > 0):
                        # Send change notification
                        self.sendChargeSessionUpdate(event='charge_session_condensed', data={ 'surviveId': charge_session.id, 'deleteId': same_charge_session_id })
                        self.sendChargeSessionUpdate(event='charge_session_data_update', data=charge_session.to_str())


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
