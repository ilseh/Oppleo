from nl.carcharging.api.TeslaApi import TeslaAPI

tesla_api = TeslaAPI()
tesla_api.authenticate('frans.laemen@kpn.com', 'pw4Tesla')
l = tesla_api.getVehicleNameIdList()
print(l)
odo = tesla_api.getOdometerWithId(l[0]['id'])
print(odo)
odo = tesla_api.getOdometerWithId(l[0]['id'])
print(odo)
print('Done!')