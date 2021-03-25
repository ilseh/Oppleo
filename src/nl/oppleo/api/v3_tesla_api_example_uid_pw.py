from getpass import getpass
import pprint
from nl.oppleo.api.TeslaApi import TeslaAPI

vehicle_index = 0

t_api = TeslaAPI()

print('Enter username: ')
username = input()
password = getpass('Password (typing not shown):')

t_auth = t_api.authenticate_v3(username, password)
valid = t_api.hasValidToken()
exp = t_api.tokenRefreshCheck()
v_list = t_api.getVehicleList()
if v_list is None:
    print('No vehicles found')
else:
    cs = t_api.getChargeStateWithId(v_list[vehicle_index]['id_s'])
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(cs)
    # print(cs)

    """
    {
        'battery_heater_on': False, 
        'battery_level': 90, 
        'battery_range': 260.15, 
        'charge_current_request': 16, 
        'charge_current_request_max': 16, 
        'charge_enable_request': True, 
        'charge_energy_added': 48.35, 
        'charge_limit_soc': 90, 
        'charge_limit_soc_max': 100, 
        'charge_limit_soc_min': 50, 
        'charge_limit_soc_std': 90, 
        'charge_miles_added_ideal': 197.5, 
        'charge_miles_added_rated': 197.5, 
        'charge_port_cold_weather_mode': False, 
        'charge_port_door_open': True, 
        'charge_port_latch': 'Engaged', 
        'charge_rate': 0.0, 
        'charge_to_max_range': False, 
        'charger_actual_current': 0, 
        'charger_phases': 2, 
        'charger_pilot_current': 16, 
        'charger_power': 0, 
        'charger_voltage': 2, 
        'charging_state': 'Stopped', 
        'conn_charge_cable': 'IEC', 
        'est_battery_range': 238.44, 
        'fast_charger_brand': '<invalid>', 
        'fast_charger_present': False, 
        'fast_charger_type': '<invalid>', 
        'ideal_battery_range': 260.15, 
        'managed_charging_active': False, 
        'managed_charging_start_time': None, 
        'managed_charging_user_canceled': False, 
        'max_range_charge_counter': 0, 
        'minutes_to_full_charge': 0, 
        'not_enough_power_to_heat': None, 
        'scheduled_charging_pending': False, 
        'scheduled_charging_start_time': None, 
        'time_to_full_charge': 0.0, 
        'timestamp': 1616683790233, 
        'trip_charging': False, 
        'usable_battery_level': 89, 
        'user_charge_enable_request': None
        }
    """

    odo = t_api.getOdometerWithId(v_list[vehicle_index]['id_s'])
    print('Odometer for vehicle {} (id:{} vin:{}) is {}km'.format(
            v_list[vehicle_index]['display_name'],
            v_list[vehicle_index]['id_s'],
            v_list[vehicle_index]['vin'],
            odo
            )
        )
pass