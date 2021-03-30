from getpass import getpass
import pprint
from datetime import datetime
from nl.oppleo.api.TeslaApi import TeslaAPI
from nl.oppleo.daemon.VehicleChargeStatusMonitorThread import VehicleChargeStatusMonitorThread

vehicle_index = 0

t_api = TeslaAPI()

username = input('Enter username: ')
password = getpass('Password (typing not shown): ')

t_auth = t_api.authenticate_v3(username, password)
requiresRefresh = t_api.tokenRequiresRefresh()
# refreshed = t_api.refreshTokenIfRequired()
v_list = t_api.getVehicleList()
if v_list is None:
    print('No vehicles found')
else:
    cs = t_api.getChargeStateWithId(v_list[vehicle_index]['id_s'])

    try:
        dt_object = datetime.fromtimestamp(cs['timestamp']/1000)
        print("timestamp=", dt_object)
    except Exception:
        print("No timestamp value")

    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(cs)

    """

    'battery_level': 74,                    --- percentage vol
    'battery_range': 215.28,                - vertaald naar range (74=215,28 90=262,29 - miles denk ik)

    'charge_energy_added': 11.41,           --> dit is wat de auto denkt te hebben geladen
                                                lader zegt 12,4 getal gaat van 11,41 naar 11,31 - schatting?
    'charge_limit_soc': 90,                 - huidige charge limiet in de app
    'charge_limit_soc_max': 100,            - max 468km in app

    'charge_port_door_open': True,
    'charge_port_latch': 'Engaged',

    'charge_rate': 43.4,                    - @ 70kmh, 3x 16A  ~48A, 0.0 bij niet laden

    'charger_actual_current': 0,            - is per fase denk ik, max 16A hier
    'charger_phases': 2,                    - ja drie dus. Nul based???
    'charger_power': 11,                    - kW
    'charger_voltage': 235,                 - V

    'charging_state': 'Charging',           - Charging, Stopped, Complete, andere statussen?

    'minutes_to_full_charge': 70,                   - 70min
    'time_to_full_charge': 1.17,                    - 1u 17min (77min)

    'timestamp': 1616709968595,

    """


    vehicle_config = t_api.getVehicleConfigWithId(v_list[vehicle_index]['id_s'])

    odo = t_api.getOdometerWithId(v_list[vehicle_index]['id_s'])
    print('Odometer for vehicle {} (id:{} vin:{}) is {}km'.format(
            v_list[vehicle_index]['display_name'],
            v_list[vehicle_index]['id_s'],
            v_list[vehicle_index]['vin'],
            odo
            )
        )

    vcsmt = VehicleChargeStatusMonitorThread()
    fvcs = vcsmt.formatChargeState(cs)

    pp.pprint(fvcs)

pass