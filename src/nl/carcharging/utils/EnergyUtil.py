import minimalmodbus
from nl.carcharging.utils.GenericUtil import GenericUtil
from nl.carcharging.models.EnergyDeviceModel import EnergyDeviceModel
import logging


class EnergyUtil:
    energy_device_id = None
    instrument = None
    appSocketIO = None
 

    def __init__(self, energy_device_id, appSocketIO=None):
        self.logger = logging.getLogger('nl.carcharging.services.EnergyUtil')
        self.energy_device_id = energy_device_id
        self.appSocketIO = appSocketIO
        self.self.initInstrument()


    def initInstrument(self):

        device_data = EnergyDeviceModel.get_one(self.energy_device_id)
        self.logger.debug(
            'found device: %s %s %d' % (device_data.energy_device_id, device_data.port_name, device_data.slave_address))

        #minimalmodbus.TIMEOUT = 2
        minimalmodbus.TIMEOUT = device_data.modbus_timeout

        self.instrument = minimalmodbus.Instrument(device_data.port_name,
                                              device_data.slave_address)  # port name, slave address (in decimal)

        # Get this from the database
        self.instrument.serial.baudrate = device_data.baudrate
        self.instrument.serial.bytesize = device_data.bytesize
        self.instrument.serial.parity = device_data.parity
        self.instrument.serial.stopbits = device_data.stopbits
        self.instrument.serial.timeout = device_data.serial_timeout
        self.instrument.debug = device_data.debug
        self.instrument.mode = device_data.mode
        self.instrument.close_port_after_each_call = device_data.close_port_after_each_call


    def getMeasurementValue(self):

        if GenericUtil.isProd():
            self.logger.debug('Production environment, getting real data')
            return self.getProdMeasurementValue()
        else:
            self.logger.debug('Not production environment, getting fake data')
            return self.getDevMeasurementValue()

    def getDevMeasurementValue(self):
        self.logger.debug('returning fake data')
        return {
            "energy_device_id": self.energy_device_id,
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

    def getProdMeasurementValue(self):

        L1_V = round(self.try_read_float('l1_v', 0, 4, 2, 0), 1)  # 30001 Phase 1 line to neutral volts. [V]
        L2_V = round(self.try_read_float('l2_v', 2, 4, 2, 0), 1)  # 30003 Phase 2 line to neutral volts. [V]
        L3_V = round(self.try_read_float('l3_v', 4, 4, 2, 0), 1)  # 30005 Phase 3 line to neutral volts. [V]

        L1_A = round(self.try_read_float('l1_a', 6, 4, 2, 0), 1)  # 30007 Phase 1 current. [A]
        L2_A = round(self.try_read_float('l2_a', 8, 4, 2, 0), 1)  # 30009 Phase 2 current. [A]
        L3_A = round(self.try_read_float('l3_a', 10, 4, 2, 0), 1)  # 30011 Phase 3 current. [A]

        L1_P = round(self.try_read_float('l1_p', 12, 4, 2, 0), 1)  # 30013 Phase 1 power. [W]
        L2_P = round(self.try_read_float('l2_p', 14, 4, 2, 0), 1)  # 30013 Phase 2 power. [W]
        L3_P = round(self.try_read_float('l3_p', 16, 4, 2, 0), 1)  # 30013 Phase 3 power. [W]

        L1_kWh = round(self.try_read_float('l1_kwh', 358, 4, 2, 0), 1)  # 300359 Phase 1 total kWh. [kWh]
        L2_kWh = round(self.try_read_float('l2_kwh', 360, 4, 2, 0), 1)  # 300361 Phase 2 total kWh. [kWh]
        L3_kWh = round(self.try_read_float('l3_kwh', 362, 4, 2, 0), 1)  # 300363 Phase 3 total kWh. [kWh]

        kWh = round(self.try_read_float('kwh', 342, 4, 2, 0), 1)  # 300343 Total kWh. [kWh]

        HZ = round(self.try_read_float('hz', 70, 4, 2, 0), 1)  # 30071 Frequency of supply voltages. [Hz]

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
            "hz": HZ
        }

    def try_read_float(self, value_desc, registeraddress, functioncode, number_of_registers, byteorder):
        value = -1
        try:
            value = self.instrument.read_float(registeraddress, functioncode, number_of_registers, byteorder)
        except Exception as ex:
            self.logger.warning("Could not read value %s, gave exception %s Using value %d" % (value_desc, ex, value))
        if self.appSocketIO is not None:
            # Yield if we can, allow other time constraint threads to run
            self.appSocketIO.sleep(0.01)
        return value
