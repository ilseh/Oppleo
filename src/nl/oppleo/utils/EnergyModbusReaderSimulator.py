import logging
import time
import random
import json

from nl.oppleo.config.OppleoSystemConfig import OppleoSystemConfig
from nl.oppleo.config.OppleoConfig import OppleoConfig
from nl.oppleo.daemon.ChargerHandlerThread import ChargerHandlerThread

oppleoSystemConfig = OppleoSystemConfig()
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

    __l1_v = 0.0  # V
    __l1_v = 0.0  # V
    __l1_a = 0.0  # A
    __l1_p = 0.0  # W
    __l1_e_u = 0.000 # kWh unrounded
    __l1_e = 0.0  # kWh
    __l2_v = 0.0  # V
    __l2_a = 0.0  # A
    __l2_p = 0.0  # W
    __l2_e_u = 0.000 # kWh unrounded
    __l2_e = 0.0  # kWh
    __l3_v = 0.0  # V
    __l3_a = 0.0  # A
    __l3_p = 0.0  # W
    __l3_e_u = 0.000 # kWh unrounded
    __l3_e = 0.0  # kWh
    __f = 0.0     # Hz       

    __v_min = 228
    __v_max = 238
    __a_min = 13
    __a_max = 16.1
    __f_min = 49.9
    __f_max = 50.1

    __a_ramp_up = 16 / 6      # 6 seconds to 16A
    __a_ramp_down = 16 / 3   # 3 seconds back to 0A


    def __init__(self, energy_device_id=None, appSocketIO=None):
        self.__logger = logging.getLogger(__name__)
        self.__logger.setLevel(level=oppleoSystemConfig.getLogLevelForModule(__name__))

        self.__energy_device_id = energy_device_id
        self.__appSocketIO = appSocketIO
        self.__lasttime = time.time()

    def __max(self, a, b):
        if a >= b:
            return a
        else:
            return b

    def __min(self, a, b):
        if a >= b:
            return a
        else:
            return b

    def __get_value(self, current_value, min:float=0, max:float=0, decimals:int=1, rampupdown:bool=False):
        global oppleoConfig

        if rampupdown:
            if oppleoConfig.chThread is None or not oppleoConfig.chThread.is_status_charging:
                # Not charging, go down or stay down
                if current_value <= 0.1:
                    # Stay down
                    return round( random.uniform(0.0, 0.1), decimals )
                # Ramp down, minimize on zero
                return self.__max( round( current_value - self.__a_ramp_down - ( (1 if random.random() < 0.5 else -1) * (self.__a_ramp_down / 10) ), decimals ), 0)
            else:
                # Charging
                if min <= current_value:
                    # Charging, stay up
                    return round( random.uniform(min, max), decimals )
                else:
                    # Charging, ramp up
                    return self.__min( round( current_value + self.__a_ramp_up + ( (1 if random.random() < 0.5 else -1) * (self.__a_ramp_up / 10) ), decimals ), max)
        # Else return number
        return round( random.uniform(min, max), decimals )

    def getMeasurementValue(self):
        self.__logger.warn('Simulator environment, getting simulated measurement')
        now = time.time()
        secondsPassed = now - self.__lasttime
        self.__l1_e_u = self.__l1_e_u + ( (secondsPassed/ 3600) * (self.__l1_p /1000) )
        self.__l1_e = round( self.__l1_e_u, 1)
        self.__l2_e_u = self.__l2_e_u + ( (secondsPassed/ 3600) * (self.__l2_p /1000) )
        self.__l2_e = round( self.__l2_e_u, 1)
        self.__l3_e_u = self.__l3_e_u + ( (secondsPassed/ 3600) * (self.__l3_p /1000) )
        self.__l3_e = round( self.__l3_e_u, 1)
        self.__l1_a = self.__get_value(current_value=self.__l1_a, min=self.__a_min, max=self.__a_max, rampupdown=True)
        self.__l2_a = self.__get_value(current_value=self.__l2_a, min=self.__a_min, max=self.__a_max, rampupdown=True)
        self.__l3_a = self.__get_value(current_value=self.__l3_a, min=self.__a_min, max=self.__a_max, rampupdown=True)
        self.__l1_v = self.__get_value(current_value=self.__l1_v, min=self.__v_min, max=self.__v_max)
        self.__l2_v = self.__get_value(current_value=self.__l2_v, min=self.__v_min, max=self.__v_max)
        self.__l3_v = self.__get_value(current_value=self.__l3_v, min=self.__v_min, max=self.__v_max)
        self.__l1_p = round( self.__l1_v * self.__l1_a, 1 )
        self.__l2_p = round( self.__l2_v * self.__l2_a, 1 )
        self.__l3_p = round( self.__l3_v * self.__l3_a, 1 )
        self.__f = self.__get_value(self.__f, self.__f_min, self.__f_max)
        reading = {
            "energy_device_id": self.__energy_device_id,
            "kwh_l1": self.__l1_e,
            "kwh_l2": self.__l2_e,
            "kwh_l3": self.__l3_e,
            "a_l1": self.__l1_a,
            "a_l2": self.__l2_a,
            "a_l3": self.__l3_a,
            "v_l1": self.__l1_v,
            "v_l2": self.__l2_v,
            "v_l3": self.__l3_v,
            "p_l1": self.__l1_p,
            "p_l2": self.__l2_p,
            "p_l3": self.__l3_p,
            "kw_total": round( self.__l1_e + self.__l2_e + self.__l3_e, 1 ),
            "hz": self.__f
        }
        self.__logger.debug('Simulating (charging:{}, interval:{}s) values {}'.format(
            (None if oppleoConfig.chThread is None else oppleoConfig.chThread.is_status_charging), 
            round(secondsPassed, 1), json.dumps(reading, default=str)))
        self.__lasttime = now
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
        oppleoConfig.kWhMeterSerial = 99999999
        return oppleoConfig.kWhMeterSerial
