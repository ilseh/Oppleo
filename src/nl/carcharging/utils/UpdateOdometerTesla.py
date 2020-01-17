import logging
import datetime

from api.teslaapi import TeslaAPI 
from nl.carcharging.models.SessionModel import SessionModel
from nl.carcharging.models.RfidModel import RfidModel

class UpdateOdometerTesla:

    def __init__(self):
        self.logger = logging.getLogger('UpdateOdometerTesla')
        self.logger.debug('UpdateOdometerTesla.__init__')

    def update_odometer(self, session_id=None):
        # This method starts a thread which grabs the odometer value and updates the session table
        if session_id == None:
            self.logger.debug("No session id")
            return
        session = SessionModel.get_one_session(session_id)
        if (session == None):
            self.logger.debug("Session with id {} not found.".format(session_id))
            return
        rfid = RfidModel.get_ome(session.rfid)
        if (rfid == None):
            self.logger.debug("Rfid {} not found.".format(rfid))
            return
        # Valid token?
        teslaApi = TeslaAPI()
        self.copy_token_from_rfid_to_api(rfid=rfid, api=teslaApi)
        if (not TeslaAPI.hasValidToken()):
            self.logger.debug("Token has expired.")
            # TODO Notify someone
            return

        # get the odometer
        session.odometer = teslaApi.getOdometer()
        session.commit()
        self.logger.debug("Obtained odometer {} for {} ".format(
            session.odometer, 
            teslaApi.vehicle_list[teslaApi.selected_vehicle][teslaApi.VEHICLE_DISPLAY_NAME_PARAM]))
        if teslaApi.checkTokenRefresh():
            # Token refreshed, store in rfid
            self.logger.debug("Token refreshed")
            self.copy_token_from_api_to_rfid(teslaApi, rfid)
            rfid.commit()
            self.logger.debug("Refreshed token stored in rfid")
        

    def copy_token_from_rfid_to_api(self, rfid, api):
        api.access_token  = rfid.api_access_token        
        api.token_type    = rfid.api_token_type        
        api.created_at    = rfid.api_created_at        
        api.expires_in    = rfid.api_expires_in        
        api.refresh_token = rfid.api_refresh_token        

    def copy_token_from_api_to_rfid(self, api, rfid):
        rfid.api_access_token  = api.access_token        
        rfid.api_token_type    = api.token_type        
        rfid.api_created_at    = api.created_at        
        rfid.api_expires_in    = api.expires_in        
        rfid.api_refresh_token = api.refresh_token        
