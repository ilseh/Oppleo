from nl.carcharging.api.TeslaApi import TeslaAPI

print('Tesla API test')
print('Tesla username (email):')
email = input()
print('Tesla password:')
password = input()

tesla_api = TeslaAPI()
tesla_api.authenticate(email, password)
l = tesla_api.getVehicleNameIdList()
print(l)
odo = tesla_api.getOdometerWithId(l[0]['id'])
print(odo)
odo = tesla_api.getOdometerWithId(l[0]['id'])
print(odo)
print('Done!')