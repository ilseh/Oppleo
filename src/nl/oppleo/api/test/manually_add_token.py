
import os
import time
from datetime import datetime, timedelta

from configparser import ConfigParser, NoSectionError, NoOptionError

from nl.oppleo.models.RfidModel import RfidModel
from nl.oppleo.api.TeslaApi import TeslaAPI

myCarFile   = 'mycar.ini'
SECTION     = 'Tesla'

TOKEN           = 'rfid'
VIN             = 'vin'

VEHICLE_ID      = 'id_s'
VEHICLE_NAME    = 'vehicle_name'

TOKEN_TYPE      = 'token_type'
ACCESS_TOKEN    = 'access_token'
CREATED_AT      = 'created_at'
EXPIRES_IN      = 'expires_in'
REFRESH_TOKEN   = 'refresh_token'


myCarFilePath = os.path.join(os.path.dirname(os.path.realpath(__file__)), myCarFile)

print('Helper to manually add Tesla OAuth token to RFID token.')
print("Reads date from {}".format(myCarFilePath))


myCar = ConfigParser()
try:
    myCar.read_file(open(myCarFilePath, "r"))
except FileNotFoundError as fnfe:
    # System configuration file not found! (Creating with defaults)
    print("Error: file not found")
    exit(0)

def getOption(iniFile, section, option, default=''):
    if not iniFile.has_option(section, option):
        return default
    return iniFile.get(section, option)

# Read the ini file
if not myCar.has_section(SECTION):
    print("File read error: No {} section".format(SECTION))
    exit(0)

token           = getOption(iniFile=myCar, section=SECTION, option=TOKEN)
vin             = getOption(iniFile=myCar, section=SECTION, option=VIN)
vehicle_id      = getOption(iniFile=myCar, section=SECTION, option=VEHICLE_ID)
vehicle_name    = getOption(iniFile=myCar, section=SECTION, option=VEHICLE_NAME)
token_type      = getOption(iniFile=myCar, section=SECTION, option=TOKEN_TYPE, default='Bearer')
token_type      = getOption(iniFile=myCar, section=SECTION, option=TOKEN_TYPE, default='Bearer')
access_token    = getOption(iniFile=myCar, section=SECTION, option=ACCESS_TOKEN)
created_at      = getOption(iniFile=myCar, section=SECTION, option=CREATED_AT, default=str( int( datetime.now().timestamp() ) ))
expires_in      = getOption(iniFile=myCar, section=SECTION, option=EXPIRES_IN, default=str( int( (timedelta(weeks=6)).total_seconds() ) ))
refresh_token   = getOption(iniFile=myCar, section=SECTION, option=REFRESH_TOKEN)



rfid_model = RfidModel().get_one(token)
if ((token == None) or (rfid_model == None)):
    print("Token {} not found".format(token))
    exit(0)


# Update for specific token
tesla_api = TeslaAPI()


# Obtained token
rfid_model.get_odometer         = True

rfid_model.vehicle_id           = vehicle_id    # The id_s from 'https://owner-api.teslamotors.com/api/1/vehicles'
rfid_model.vehicle_vin          = vin
rfid_model.vehicle_name         = vehicle_name

rfid_model.api_access_token     = access_token
rfid_model.api_token_type       = token_type
rfid_model.api_created_at       = created_at
rfid_model.api_expires_in       = expires_in
rfid_model.api_refresh_token    = refresh_token

rfid_model.save()

print("Token {} updated.".format(token))
