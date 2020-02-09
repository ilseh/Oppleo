import minimalmodbus
from nl.carcharging.utils.GenericUtil import GenericUtil
from nl.carcharging.models.EnergyDeviceModel import EnergyDeviceModel
import logging


class EnergyUtil:

    def __init__(self):
        self.logger = logging.getLogger('nl.carcharging.services.EnergyUtil')

    def initInstrument(self, energy_device_id):

        device_data = EnergyDeviceModel.get_one(energy_device_id)
        self.logger.debug(
            'found device: %s %s %d' % (device_data.energy_device_id, device_data.port_name, device_data.slave_address))

        minimalmodbus.TIMEOUT = 2
        instrument = minimalmodbus.Instrument(device_data.port_name,
                                              device_data.slave_address)  # port name, slave address (in decimal)
        instrument.close_port_after_each_call = True

        # TODO get this from the database

        instrument.serial.baudrate = 9600
        instrument.serial.bytesize = 8
        instrument.serial.parity = minimalmodbus.serial.PARITY_NONE
        instrument.serial.stopbits = 1
        instrument.serial.timeout = 1
        instrument.debug = False
        instrument.mode = minimalmodbus.MODE_RTU

        return instrument

    def getMeasurementValue(self, energy_device_id):

        if GenericUtil.isProd():
            self.logger.debug('Production environment, getting real data')
            return self.getProdMeasurementValue(energy_device_id)
        else:
            self.logger.debug('Not production environment, getting fake data')
            return self.getDevMeasurementValue(energy_device_id)

    def getDevMeasurementValue(self, energy_device_id):
        self.logger.debug('returning fake data')
        return {
            "energy_device_id": energy_device_id,
            "kwh_l1": 1532.34,
            "kwh_l2": 1542.34,
            "kwh_l3": 1534.34,
            "a_l1": 534.34,
            "a_l2": 534.34,
            "a_l3": 534.34,
            "v_l1": 1,
            "v_l2": 2,
            "v_l3": 3,
            "p_l1": 1,
            "p_l2": 2,
            "p_l3": 3,
            "kw_total": 50034.34,
            "hz": 60034.34,
        }

    def getProdMeasurementValue(self, energy_device_id):

        instrument = self.initInstrument(energy_device_id)

        L1_V = round(self.try_read_float('l1_v', instrument, 0, 4, 2, 0), 1)  # 30001 Phase 1 line to neutral volts. [V]
        L2_V = round(self.try_read_float('l2_v', instrument, 2, 4, 2, 0), 1)  # 30003 Phase 2 line to neutral volts. [V]
        L3_V = round(self.try_read_float('l3_v', instrument, 4, 4, 2, 0), 1)  # 30005 Phase 3 line to neutral volts. [V]

        L1_A = round(self.try_read_float('l1_a', instrument, 6, 4, 2, 0), 1)  # 30007 Phase 1 current. [A]
        L2_A = round(self.try_read_float('l2_a', instrument, 8, 4, 2, 0), 1)  # 30009 Phase 2 current. [A]
        L3_A = round(self.try_read_float('l3_a', instrument, 10, 4, 2, 0), 1)  # 30011 Phase 3 current. [A]

        L1_P = round(self.try_read_float('l1_p', instrument, 12, 4, 2, 0), 1)  # 30013 Phase 1 power. [W]
        L2_P = round(self.try_read_float('l2_p', instrument, 14, 4, 2, 0), 1)  # 30013 Phase 2 power. [W]
        L3_P = round(self.try_read_float('l3_p', instrument, 16, 4, 2, 0), 1)  # 30013 Phase 3 power. [W]

        L1_kWh = round(self.try_read_float('l1_kwh', instrument, 358, 4, 2, 0), 1)  # 300359 Phase 1 total kWh. [kWh]
        L2_kWh = round(self.try_read_float('l2_kwh', instrument, 360, 4, 2, 0), 1)  # 300361 Phase 2 total kWh. [kWh]
        L3_kWh = round(self.try_read_float('l3_kwh', instrument, 362, 4, 2, 0), 1)  # 300363 Phase 3 total kWh. [kWh]

        kWh = round(self.try_read_float('kwh', instrument, 342, 4, 2, 0), 1)  # 300343 Total kWh. [kWh]

        HZ = round(self.try_read_float('hz', instrument, 70, 4, 2, 0), 1)  # 30071 Frequency of supply voltages. [Hz]

        # Close instrument?

        return {
            "energy_device_id": energy_device_id,
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
            "hz": HZ
        }

    def try_read_float(self, value_desc, instrument, registeraddress, functioncode, number_of_registers, byteorder):
        value = -1
        try:
            value = instrument.read_float(registeraddress, functioncode, number_of_registers, byteorder)
        except Exception as ex:
            self.logger.warning("Could not read value %s, gave exception %s Using value %d" % (value_desc, ex, value))

        return value
