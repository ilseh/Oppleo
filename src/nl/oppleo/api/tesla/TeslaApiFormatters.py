import re


def toCamelcase(s):
    return re.sub(r'(?!^)_([a-zA-Z])', lambda m: m.group(1).upper(), s)

def milesToKm(miles:float=0, acc:int=0):
    return round(miles * 1.609344 * pow(10, acc)) / pow(10, acc)

def formatTeslaChargeStateParam(chargeState:dict=None, param:str=None):
    if chargeState is None or param is None or param not in chargeState:
        return chargeState
    try:
        return chargeState[param]
    except:
        return None




"""
    id                          identifier for the car on the owner-api endpoint
    id_s                        string version of the id
    vehicle_id                  identifying the car across different endpoints, such as the streaming or Autopark APIs.
                                Oppleo uses the id_s and stores it as vehicle_id in the RFID 8)
    battery_level               battery percentage charged [int]
    battery_range               range in miles with current battery level [int]
    charge_energy_added         enery added in the charge session of the vehicle, in kWh [int]
    charge_limit_soc            charge limit percentage set [int]
    charge_limit_soc_max        max charge limit [int]
    charge_port_door_open       [True | False],
    charge_rate                 miles per hout [float]
    charger_actual_current      amps
    charger_phases              2 for three phases? [int]
    charger_power               in kW 
    charger_voltage             [Volts]
    charging_state              [Charging, Stopped, Complete, Disconnected]
    minutes_to_full_charge      70 [int] 
    time_to_full_charge         A value of 1.17 indicates 1.17 * 60min = 1u 10min = 70min [float]
    timestamp                   in millis
"""
def formatTeslaChargeState(chargeState:dict=None) -> dict:
    csEl = ['battery_level', 'battery_range', 'charge_energy_added', 'charge_limit_soc', 'charge_limit_soc_max', 
            'charge_miles_added_rated', 'charge_port_door_open', 'charge_port_latch', 'charge_rate', 'charger_actual_current', 'charger_phases',
            'charger_power', 'charger_voltage', 'charging_state', 'minutes_to_full_charge', 'time_to_full_charge', 
            'est_battery_range', 'ideal_battery_range', 'timestamp']

    # Which ones are in miles
    csElMiles = ['battery_range', 'charge_miles_added_rated', 'charge_rate', 'est_battery_range', 'ideal_battery_range']
    # Corresponding km variables
    csElKm = ['battery_range', 'charge_km_added_rated', 'charge_rate', 'est_battery_range', 'ideal_battery_range']
    if chargeState is None:
        return {}

    csDict = {}
    for el in csEl:
        csDict[toCamelcase(el)] = formatTeslaChargeStateParam(chargeState, el)
        if el in csElMiles and isinstance(csDict[toCamelcase(el)], float):
            # Convert type(csDict[toCamelcase(el)])
            csDict[toCamelcase(csElKm[csElMiles.index(el)])] = milesToKm(csDict[toCamelcase(el)], 1)
            if el != csElKm[csElMiles.index(el)]:
                # Only delete if it was stored on a different key
                del csDict[toCamelcase(el)]

    return csDict

"""

{
    "batteryLevel": 90,
    "batteryRange": 420.7,
    "chargeEnergyAdded": 4.92,
    "chargeKmAddedRated": 32.2,
    "chargeLimitSoc": 90,
    "chargeLimitSocMax": 100,
    "chargePortDoorOpen": true,
    "chargePortLatch": "Engaged",
    "chargeRate": 0,
    "chargerActualCurrent": 0,
    "chargerPhases": 2,
    "chargerPower": 0,
    "chargerVoltage": 2,
    "chargingState": "Stopped",
    "minutesToFullCharge": 0,
    "timeToFullCharge": 0,
    "timestamp": 1617095513483
}
"""

# https://tesla-api.timdorr.com/vehicle/optioncodes
def battCapacityFromTeslaOptionCodes(optionCodes:str=None) -> int:
    ocMap = { 'BT37': 75,
              'BT40': 40,
              'BT60': 60,
              'BT70': 70,
              'BT85': 85,
              'BTX4': 90,
              'BTX5': 75,
              'BTX6': 100,
              'BTX7': 75,
              'BTX8': 75
            }

    if optionCodes is None:
        return 0
    ocl = optionCodes.split(',')
    for oc in ocl:
        if oc in ocMap and ocMap[oc] is not None:
            return ocMap[oc]
    return 0


def formatTeslaVehicle(vehicle=None):
    # Elements in vehicle
    csEl = ['id_s', 'vin', 'display_name', 'option_codes', 'timestamp', 'state']

    if vehicle is None:
        return {}

    csDict = {}
    for el in csEl:
        csDict[toCamelcase(el)] = formatTeslaChargeStateParam(vehicle, el)

    if 'option_codes' in vehicle and vehicle['option_codes'] is not None:
        bc = battCapacityFromTeslaOptionCodes(vehicle['option_codes'])
        if bc > 0:
            csDict['batteryCapacity'] = bc

    return csDict
