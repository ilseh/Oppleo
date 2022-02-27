from nl.oppleo.models.RfidModel import RfidModel
from nl.oppleo.api.VehicleApi import VehicleApi
from nl.oppleo.api.tesla.TeslaApiFormatters import formatTeslaVehicle, formatTeslaChargeState

token = "856853722117"

if __name__ == "__main__":

    rfid_model = RfidModel.get_one(rfid=token)

    vApi = VehicleApi(rfid_model=rfid_model)

    img = vApi.composeImage()

    awake = vApi.isAwake()
    print ("awake: {}".format(awake))

    odo = vApi.getOdometer()
    print ("odo: {}".format(odo))

    vd = vApi.getVehicleData()
    print ("vd: {}".format(vd))
    print ("formatTeslaVehicle(vd): {}".format(formatTeslaVehicle(vd)))

    cs = vApi.getChargeState()
    print ("cs: {}".format(cs))
    print ("formatTeslaChargeState(cs): {}".format(formatTeslaChargeState(cs)))


print ("Done")