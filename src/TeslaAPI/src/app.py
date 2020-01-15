# importing the requests library 
from teslaapi import TeslaAPI 

teslaapi = TeslaAPI()
odometer = teslaapi.getOdometer()
if (odometer is not None):
    print("Odometer is {}".format(int(odometer)))
