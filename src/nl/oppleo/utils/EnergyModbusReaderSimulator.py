import logging
from datetime import datetime, timedelta
import random

from nl.oppleo.config.OppleoConfig import OppleoConfig

oppleoConfig = OppleoConfig()

"""
    DEBUG DEVICE 
    - Debug device mimicing the behaviour of the EnergyDevice


        EnergyModbusReader.readSerialNumber
            self.oppleoConfig.kWhMeterSerial = 99999999

        EnergyModbusReader.getMeasurementValue(self):
 
        return {
            "energy_device_id": self.energy_device_id,
            "kwh_l1": L1_kWh,
            "kwh_l2": L2_kWh,
            "kwh_l3": L3_kWh,
            "a_l1": L1_A,
            "a_l2": L2_A,
            "a_l3": L3_A,
            "v_l1": L1_V,
            "v_l2": L2_V,
            "v_l3": L3_V,
            "p_l1": L1_P,
            "p_l2": L2_P,
            "p_l3": L3_P,
            "kw_total": kWh,
            "hz": Hz
        }
"""

class EnergyModbusReaderSimulator():

    __logger = None

    __energy_device_id = None
    __appSocketIO = None
    __lasttime = 0

    __l1_v = 0.0,  # V
    __l1_v = 0.0,  # V
    __l1_a = 0.0,  # A
    __l1_p = 0.0,  # W
    __l1_e = 0.0,  # kWh
    __l2_v = 0.0,  # V
    __l2_a = 0.0,  # A
    __l2_p = 0.0,  # W
    __l2_e = 0.0,  # kWh
    __l3_v = 0.0,  # V
    __l3_a = 0.0,  # A
    __l3_p = 0.0,  # W
    __l3_e = 0.0,  # kWh
    __f = 0.0,     # Hz       

    __v_min = 218,
    __v_max = 233,
    __a_min = 13,
    __a_max = 16.1,
    __f_min = 49.9
    __f_max = 50.1

    __a_ramp_up = 16 / 6      # 6 seconds to 16A
    __a_ramp_down = 16 / 3   # 3 seconds back to 0A

    __charging_enabled = False

    def __init__(self, energy_device_id=None, appSocketIO=None):
        self.__logger = logging.getLogger('nl.oppleo.daemon.EnergyModbusReaderSimulator')
        self.__energy_device_id = energy_device_id
        self.__appSocketIO = appSocketIO
        self.__lasttime = datetime.now()

    def __get_value(self, current_value, min:float=0, max:float=0, decimals:int=1, rampupdown:bool=False):
        if rampupdown:
            if not self.__charging_enabled:
                # Stay down
                if current_value <= 0.1:
                    return round( random.uniform(0.0, 0.1), decimals )
                # Ramp down
                return current_value - self.__a_ramp_down
            else:
                if current_value in range(min, max):
                    # Stay op
                    return round( random.uniform(min, max), decimals )
                else:
                    # Ramp up
                    return current_value + self.__a_ramp_up
        # Else return number
        return round( random.uniform(min, max), decimals )

    def getMeasurementValue(self):
        self.__logger.warn('Simulator environment, getting simulated measurtement')
        now = datetime.now()
        time = now - self.__lasttime
        reading = {
            "energy_device_id": self.__energy_device_id,
            "kwh_l1": round( self.__l1_e + ( (time / timedelta(hour=1)) * self.__l1_p ), 1),
            "kwh_l2": round( self.__l2_e + ( (time / timedelta(hour=1)) * self.__l2_p ), 1),
            "kwh_l3": round( self.__l3_e + ( (time / timedelta(hour=1)) * self.__l3_p ), 1),
            "a_l1": self.__get_value(current_value=self.__l1_a, min=self.__a_min, max=self.__a_max, rampupdown=True),
            "a_l2": self.__get_value(current_value=self.__l1_a, min=self.__a_min, max=self.__a_max, rampupdown=True),
            "a_l3": self.__get_value(current_value=self.__l1_a, min=self.__a_min, max=self.__a_max, rampupdown=True),
            "v_l1": self.__get_value(current_value=self.__l1_v, min=self.__v_min, max=self.__v_max),
            "v_l2": self.__get_value(current_value=self.__l2_v, min=self.__v_min, max=self.__v_max),
            "v_l3": self.__get_value(current_value=self.__l3_v, min=self.__v_min, max=self.__v_max),
            "p_l1": round( self.__l1_v * self.__l1_a, 1 ),
            "p_l2": round( self.__l2_v * self.__l2_a, 1 ),
            "p_l3": round( self.__l3_v * self.__l3_a, 1 ),
            "kw_total": self.__l1_e + self.__l2_e + self.__l3_e,
            "hz": self.__get_value(self.__f, self.__f_min, self.__f_max)
        }
        self.__lasttime = datetime.now()
        return reading

    def getTotalKWHHValue(self):
        self.__logger.warn('Simulator environment, getting simulated data')
        return self.__l1_e + self.__l2_e + self.__l3_e

    def initInstrument(self):
        self.__logger.warn('Simulator environment, initiating simulator')
        self.readSerialNumber()

    def readSerialNumber(self, port_name=None, slave_address=None):
        global oppleoConfig

        self.__logger.warn('Simulator environment, getting simulated serial number')
        self.oppleoConfig.kWhMeterSerial = 99999999
        return self.oppleoConfig.kWhMeterSerial

    def charging_enabled(self, enabled:bool=False):
        self.__charging_enabled = enabled

