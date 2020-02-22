from nl.carcharging.api.TeslaApi import TeslaAPI

t_api = TeslaAPI()

t_auth = t_api.authenticate("frans.laemen@kpn.com", "pw4Tesla")
valid = t_api.hasValidToken()
exp = t_api.tokenRefreshCheck()
v_list = t_api.getVehicleList()

odo = t_api.getOdometerWithId("31162125672191006")

i = 0
