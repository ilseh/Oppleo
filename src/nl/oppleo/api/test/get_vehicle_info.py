from nl.oppleo.models.RfidModel import RfidModel
from nl.oppleo.api.VehicleApi import VehicleApi
from nl.oppleo.api.tesla.TeslaApiFormatters import formatTeslaVehicle, formatTeslaChargeState
import json

token = "12345"

if __name__ == "__main__":

    rfid_model = RfidModel.get_one(rfid=token)

    vApi = VehicleApi(rfid_model=rfid_model)

  #  img = vApi.composeImage()

    awake = vApi.isAwake()
    print ("awake: {}".format(awake))

    vd = vApi.getVehicleData()
    print ("vd: {}".format(json.dumps(vd, indent=4)))
    fvd = formatTeslaVehicle(vd)
    print ("formatTeslaVehicle(vd): {}".format(json.dumps(fvd, indent=4, default=str)))
 
    cs = vApi.getChargeState()
    print ("cd: {}".format(json.dumps(cs, indent=4)))
    fcs = formatTeslaVehicle(cs)
    print ("formatTeslaChargeState(cs): {}".format(json.dumps(fcs, indent=4, default=str)))

    """ 
      wakes up vehicle
    """
    odo = vApi.getOdometer()
    print ("odo: {}".format(odo))

    vd = vApi.getVehicleData()
    print ("vd: {}".format(json.dumps(vd, indent=4)))
    fvd = formatTeslaVehicle(vd)
    print ("formatTeslaVehicle(vd): {}".format(json.dumps(fvd, indent=4, default=str)))
 
    cs = vApi.getChargeState()
    print ("cd: {}".format(json.dumps(cs, indent=4)))
    fcs = formatTeslaVehicle(cs)
    print ("formatTeslaChargeState(cs): {}".format(json.dumps(fcs, indent=4, default=str)))

print ("Done")