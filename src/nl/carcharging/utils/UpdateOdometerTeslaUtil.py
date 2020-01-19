import logging
import datetime
from flask_socketio import SocketIO

from config import WebAppConfig

from nl.carcharging.api.TeslaApi import TeslaAPI 
from nl.carcharging.models.ChargeSessionModel import ChargeSessionModel
from nl.carcharging.models.RfidModel import RfidModel


"""
 Instantiate object
 Set the session id
 call start on it
"""

class UpdateOdometerTeslaUtil:
    charge_session_id = None

    def __init__(self):
        self.logger = logging.getLogger('UpdateOdometerTesla')
        self.logger.debug('UpdateOdometerTesla.__init__')
        self.thread = None

    def set_charge_session_id(self, charge_session_id=None):
        self.charge_session_id = charge_session_id

    def start(self):
        self.logger.debug(f'{datetime.datetime.now()} - Launching background task...')
        self.thread = WebAppConfig.socketio.start_background_task(self.update_odometer)

    def update_odometer(self):
        # This method starts a thread which grabs the odometer value and updates the session table
        if self.charge_session_id == None:
            self.logger.debug("No session id")
            return
        charge_session = ChargeSessionModel.get_one_charge_session(self.charge_session_id)
        if (charge_session == None):
            self.logger.debug("Session with id {} not found.".format(self.charge_session_id))
            return
        rfid_model = RfidModel.get_one(charge_session.rfid)
        if (rfid_model == None):
            self.logger.debug("Rfid {} not found.".format(charge_session.rfid))
            return
        # Valid token?
        tApi = TeslaAPI()
        self.copy_token_from_rfid_model_to_api(rfid_model=rfid_model, testla_api=tApi)
        if (not tApi.hasValidToken()):
            self.logger.debug("Token has expired.")
            # TODO Notify someone
            return

        # get the odometer
        charge_session.odometer = tApi.getOdometer()
        charge_session.commit()
        self.logger.debug("Obtained odometer {} for {} ".format(
            charge_session.odometer, 
            tApi.vehicle_list[tApi.selected_vehicle][tApi.VEHICLE_DISPLAY_NAME_PARAM]))
        if tApi.checkTokenRefresh():
            # Token refreshed, store in rfid
            self.logger.debug("Token refreshed")
            self.copy_token_from_api_to_rfid_model(tApi, rfid_model)
            rfid_model.commit()
            self.logger.debug("Refreshed token stored in rfid")
        

    def copy_token_from_rfid_model_to_api(self, rfid_model, testla_api):
        testla_api.access_token  = rfid_model.api_access_token        
        testla_api.token_type    = rfid_model.api_token_type        
        testla_api.created_at    = rfid_model.api_created_at        
        testla_api.expires_in    = rfid_model.api_expires_in        
        testla_api.refresh_token = rfid_model.api_refresh_token        

    def copy_token_from_api_to_rfid_model(self, testla_api, rfid_model):
        rfid_model.api_access_token  = testla_api.access_token        
        rfid_model.api_token_type    = testla_api.token_type        
        rfid_model.api_created_at    = testla_api.created_at        
        rfid_model.api_expires_in    = testla_api.expires_in        
        rfid_model.api_refresh_token = testla_api.refresh_token        
