from getpass import getpass
from nl.carcharging.api.TeslaApi import TeslaAPI

vehicle_index = 0

t_api = TeslaAPI()

print('Enter username: ')
username = input()
password = getpass('Password (typing not shown):')

t_auth = t_api.authenticate(username, password)
valid = t_api.hasValidToken()
exp = t_api.tokenRefreshCheck()
v_list = t_api.getVehicleList()
if v_list is None:
    print('No vehicles found')
else:
    odo = t_api.getOdometerWithId(v_list[vehicle_index]['id_s'])
    print('Odometer for vehicle {} (id:{} vin:{}) is {}km'.format(
            v_list[vehicle_index]['display_name'],
            v_list[vehicle_index]['id_s'],
            v_list[vehicle_index]['vin'],
            odo
            )
        )
pass