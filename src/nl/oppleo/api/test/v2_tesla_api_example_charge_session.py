from flask import Flask
from flask_socketio import SocketIO
from nl.oppleo.config.OppleoConfig import OppleoConfig
from nl.oppleo.utils.UpdateOdometerTeslaUtil import UpdateOdometerTeslaUtil

"""
 This is an example using the UpdateOdometerTeslaUtil helper class to 
 update the charge session in the database with the odometer (km stand)
 at this moment.
 
 It fetches the RFID from the charge session, checks for an active 
 OAuth token and uses that to login, get's the selected vehicle from the 
 RFID and fetches the odo value. This value is added to the charge session.
 
 This should be run at the start of the charge session

 The TeslaApi is quite slow, so the helper creates a thread and executes in 
 its own thread. It needs to run in an environment where this is allowed and
 threads are enabled.
 """
oppleoConfig = OppleoConfig()

# app initiliazation
app = Flask(__name__)
# Make it available through oppleoConfig
oppleoConfig.app = app
appSocketIO = SocketIO(app)
# Make it available through oppleoConfig
oppleoConfig.appSocketIO = appSocketIO


# Instantiate the helper object
uotu = UpdateOdometerTeslaUtil()
# Hand it the session id, the id from ChargeSessionModel
# This example uses 12 as this is the oldest in the local database
uotu.charge_session_id = 194
# Start the helper.
uotu.start()

    