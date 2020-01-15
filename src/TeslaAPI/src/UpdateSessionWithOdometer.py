
from teslaapi import TeslaAPI 

class UpdateSession:

    def __init__(self):
        self.logger = logging.getLogger('UpdateSession')
        self.logger.debug('UpdateSession.__init__')

    def update_odometer(self, session_id=None):
        # This method starts a thread which grabs the odometer value and updates the session table
        
