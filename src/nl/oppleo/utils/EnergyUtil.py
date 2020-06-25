import minimalmodbus
import threading

from nl.oppleo.config.OppleoConfig import OppleoConfig

from nl.oppleo.utils.GenericUtil import GenericUtil
from nl.oppleo.models.EnergyDeviceModel import EnergyDeviceModel
import logging

# https://minimalmodbus.readthedocs.io/en/stable/modbusdetails.html
MODBUS_FUNCTION_CODE_DISCRETE = 2
MODBUS_FUNCTION_CODE_HOLDING  = 3
MODBUS_FUNCTION_CODE_INPUT    = 4

# Eastron SDM630-Modbus MID V2, 3 Fase kWh meter met Modbus RS485 100A   € 139
from nl.oppleo.utils.modbus.SDM360v2 import SDM630v2
# Eastron SDM120-Modbus MID, 1 Fase kWh energie meter 45A LCD MID        €  52
from nl.oppleo.utils.modbus.SDM120 import SDM120

modbusConfigOptions = [ SDM630v2, SDM120 ]


class EnergyUtil:
    energy_device_id = None
    instrument = None
    appSocketIO = None
    modbusConfig = None
 
    def __init__(self, energy_device_id, appSocketIO=None):
        self.logger = logging.getLogger('nl.oppleo.services.EnergyUtil')
        self.energy_device_id = energy_device_id
        self.appSocketIO = appSocketIO
        self.oppleoConfig = OppleoConfig()
        if GenericUtil.isProd():
            self.logger.debug('Production environment, calling initInstrument()')
            self.initInstrument()
        else:
            self.logger.debug('Not production environment, skip initInstrument()')
        self.threadLock = threading.Lock()


    def initInstrument(self):
        global minimalmodbus, SDM630v2, SDM120

        device_data = EnergyDeviceModel.get()
        self.logger.debug(
            'found device: %s %s %d' % (device_data.energy_device_id, device_data.port_name, device_data.slave_address))

        #minimalmodbus.TIMEOUT = 2
        minimalmodbus.TIMEOUT = device_data.modbus_timeout

        self.instrument = minimalmodbus.Instrument(device_data.port_name,
                                              device_data.slave_address)

        # Get this from the database
        self.instrument.serial.baudrate = device_data.baudrate
        self.instrument.serial.bytesize = device_data.bytesize
        self.instrument.serial.parity = device_data.parity
        self.instrument.serial.stopbits = device_data.stopbits
        self.instrument.serial.timeout = device_data.serial_timeout
        self.instrument.debug = device_data.debug
        self.instrument.mode = device_data.mode
        self.instrument.close_port_after_each_call = device_data.close_port_after_each_call

        self.modbusConfig = SDM630v2
        for i in range(len(modbusConfigOptions)): 
            if device_data.modbus_config == modbusConfigOptions[i]['name']:
                self.modbusConfig = modbusConfigOptions[i]
        self.logger.debug("Modbus config {} selected (default: {}).".format(self.modbusConfig['name'], SDM630v2['name']))

        self.readSerialNumber(device_data.port_name, device_data.slave_address)


    def readSerialNumber(self, port_name=None, slave_address=None):
        self.logger.debug('readSerialNumber()')

        if self.modbusConfig['serialNumber']['enabled']:
            if self.modbusConfig['serialNumber']['type'] == "register":
                serial_Hi = self.instrument.read_register(  \
                                self.modbusConfig['serialNumber']['Hi']['ra'],  \
                                self.modbusConfig['serialNumber']['Hi']['nod'], \
                                self.modbusConfig['serialNumber']['Hi']['fc'],  \
                                self.modbusConfig['serialNumber']['Hi']['s']    \
                                )
                serial_Lo = self.instrument.read_register(  \
                                self.modbusConfig['serialNumber']['Lo']['ra'],  \
                                self.modbusConfig['serialNumber']['Lo']['nod'], \
                                self.modbusConfig['serialNumber']['Lo']['fc'],  \
                                self.modbusConfig['serialNumber']['Lo']['s']    \
                                )
                self.logger.debug('readSerialNumber() serial_Hi:{} serial_Lo:{}'.format(serial_Hi, serial_Lo))     
                self.oppleoConfig.kWhMeter_serial = str((serial_Hi * 65536 ) + serial_Lo)
                self.logger.info('kWh meter serial number: {} (port:{}, address:{})'.format(
                        self.oppleoConfig.kWhMeter_serial,
                        port_name,
                        slave_address
                        )
                    )     
            else:
                self.logger.warn('modbusConfig serialNumber type {} not supported!'.format(self.modbusConfig['serialNumber']['type']))
                self.oppleoConfig.kWhMeter_serial = 99999999
        else:
            self.oppleoConfig.kWhMeter_serial = 99999999

        return self.oppleoConfig.kWhMeter_serial

 
    def readSerialNumber_OLD(self, port_name=None, slave_address=None):
        self.logger.debug('readSerialNumber()')
        # registeraddress, number_of_decimals=0, functioncode=3, signed=False
        # Register                Hi  Lo  byte
        # 40043 Serial Number Hi  00  2A  Read the first product serial number.
        serial_Hi = self.instrument.read_register(42, 0, MODBUS_FUNCTION_CODE_HOLDING, False)
        # 40045 Serial Number Lo  00  2C  Read the second product serial number.
        serial_Lo = self.instrument.read_register(44, 0, MODBUS_FUNCTION_CODE_HOLDING, False)
        self.logger.debug('readSerialNumber() serial_Hi:{} serial_Lo:{}'.format(serial_Hi, serial_Lo))     
        self.oppleoConfig.kWhMeter_serial = str((serial_Hi * 65536 ) + serial_Lo)
        self.logger.info('kWh meter serial number: {} (port:{}, address:{})'.format(
                self.oppleoConfig.kWhMeter_serial,
                port_name,
                slave_address
                )
            )     
        return self.oppleoConfig.kWhMeter_serial


    def getTotalKWHHValue(self):
        if GenericUtil.isProd():
            self.logger.debug('Production environment, getting real data')
            return self.getProdTotalKWHHValue()
        else:
            self.logger.debug('Not production environment, getting fake data')
            return self.getDevTotalKWHHValue()

    def getMeasurementValue(self):

        if GenericUtil.isProd():
            self.logger.debug('Production environment, getting real data')
            return self.getProdMeasurementValue()
        else:
            self.logger.debug('Not production environment, getting fake data')
            return self.getDevMeasurementValue()

    def getDevTotalKWHHValue(self):
        return 50034.34

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


    def getProdTotalKWHHValue(self):
        if self.modbusConfig['total_kWh']['type'] == "float":
            return round(                               \
                self.try_read_float(                    \
                    'kwh',                              \
                    self.modbusConfig['total_kWh']['ra'],     \
                    self.modbusConfig['total_kWh']['fc'],     \
                    self.modbusConfig['total_kWh']['nor'],    \
                    self.modbusConfig['total_kWh']['bo']      \
                    ),                                  \
                1                                       \
                )
        else:
            self.logger.warn('modbusConfig total_kWh type {} not supported!'.format(self.modbusConfig['total_kWh']['type']))
            return 0


    def getProdTotalKWHHValue_OLD(self):
        return round(self.try_read_float('kwh', 342, 4, MODBUS_FUNCTION_CODE_DISCRETE, 0), 1)       # 30343 Total kWh. [kWh]



    def try_read_float_from_config(self, name, el):
        self.logger.debug("try_read_float_from_config name:{} el:{}".format(name, str(el)))

        if not el['enabled']:
            self.logger.debug("Modbus element {} not enabled".format(name))
            return 0
        if el['type'] != "float":
            self.logger.warn("Type {} for modbus element {} not supported (must be float)".format(el['type'], name))
            return 0
        return round( self.try_read_float( name, el['ra'], el['fc'], el['nor'], el['bo'] ), 1 )
        

    def getProdMeasurementValue(self):
        self.logger.debug("getProdMeasurementValue()")

        self.logger.debug("getProdMeasurementValue() l1_p {}".format(str(self.modbusConfig['L1']['P'])))
        L1_P = self.try_read_float_from_config( 'l1_p', self.modbusConfig['L1']['P'] )
        self.logger.debug("getProdMeasurementValue() l1_v {}".format(str(self.modbusConfig['L1']['V'])))
        L1_V = self.try_read_float_from_config( 'l1_v', self.modbusConfig['L1']['V'] )
        L1_A = self.try_read_float_from_config( 'l1_a', self.modbusConfig['L1']['A'] )
        L1_kWh = self.try_read_float_from_config( 'l1_kWh', self.modbusConfig['L1']['kWh'] )

        L2_P = self.try_read_float_from_config( 'l2_p', self.modbusConfig['L2']['P'] )
        L2_V = self.try_read_float_from_config( 'l2_v', self.modbusConfig['L2']['V'] )
        L2_A = self.try_read_float_from_config( 'l2_a', self.modbusConfig['L2']['A'] )
        L2_kWh = self.try_read_float_from_config( 'l2_kWh', self.modbusConfig['L2']['kWh'] )

        L3_P = self.try_read_float_from_config( 'l3_p', self.modbusConfig['L3']['P'] )
        L3_V = self.try_read_float_from_config( 'l3_v', self.modbusConfig['L3']['V'] )
        L3_A = self.try_read_float_from_config( 'l3_a', self.modbusConfig['L3']['A'] )
        L3_kWh = self.try_read_float_from_config( 'l3_kWh', self.modbusConfig['L3']['kWh'] )

        kWh = self.try_read_float_from_config( 'kWh', self.modbusConfig['total_kWh'] )
        Hz = self.try_read_float_from_config( 'hz', self.modbusConfig['Hz'] )

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

    def getProdMeasurementValue_OLD(self):

        # Register Hi  Lo
        # 30001     0   0  Phase 1 line to neutral volts. [V]
        L1_V = round(self.try_read_float('l1_v', 0, 4, MODBUS_FUNCTION_CODE_DISCRETE, 0), 1)        
        # 30003     0   2  Phase 2 line to neutral volts. [V]
        L2_V = round(self.try_read_float('l2_v', 2, 4, MODBUS_FUNCTION_CODE_DISCRETE, 0), 1)
        # 30005     0   4  Phase 3 line to neutral volts. [V]
        L3_V = round(self.try_read_float('l3_v', 4, 4, MODBUS_FUNCTION_CODE_DISCRETE, 0), 1)
        
        # 30007 Phase 1 current. [A]
        L1_A = round(self.try_read_float('l1_a', 6, 4, MODBUS_FUNCTION_CODE_DISCRETE, 0), 1)        
        # 30009 Phase 2 current. [A]
        L2_A = round(self.try_read_float('l2_a', 8, 4, MODBUS_FUNCTION_CODE_DISCRETE, 0), 1)        
        # 30011 Phase 3 current. [A]
        L3_A = round(self.try_read_float('l3_a', 10, 4, MODBUS_FUNCTION_CODE_DISCRETE, 0), 1)       
        
        # 30013 Phase 1 power. [W]
        L1_P = round(self.try_read_float('l1_p', 12, 4, MODBUS_FUNCTION_CODE_DISCRETE, 0), 1)
        # 30015 Phase 2 power. [W]
        L2_P = round(self.try_read_float('l2_p', 14, 4, MODBUS_FUNCTION_CODE_DISCRETE, 0), 1)
        # 30017 Phase 3 power. [W]
        L3_P = round(self.try_read_float('l3_p', 16, 4, MODBUS_FUNCTION_CODE_DISCRETE, 0), 1)
        
        # 30359 Phase 1 total kWh. [kWh]
        L1_kWh = round(self.try_read_float('l1_kwh', 358, 4, MODBUS_FUNCTION_CODE_DISCRETE, 0), 1)
        # 30361 Phase 2 total kWh. [kWh]
        L2_kWh = round(self.try_read_float('l2_kwh', 360, 4, MODBUS_FUNCTION_CODE_DISCRETE, 0), 1)  
        # 30363 Phase 3 total kWh. [kWh]
        L3_kWh = round(self.try_read_float('l3_kwh', 362, 4, MODBUS_FUNCTION_CODE_DISCRETE, 0), 1)  
        
        # 30343   1   56   Total kWh. [kWh]
        kWh = round(self.try_read_float('kwh', 342, 4, MODBUS_FUNCTION_CODE_DISCRETE, 0), 1)
        
        # 30071 Frequency of supply voltages. [Hz]
        HZ = round(self.try_read_float('hz', 70, 4, MODBUS_FUNCTION_CODE_DISCRETE, 0), 1)

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
        # Used by MeasureElectricityUsageThread and ChargerHandlerThread
        with self.threadLock:
            try:
                value = self.instrument.read_float(registeraddress, functioncode, number_of_registers, byteorder)
            except Exception as ex:
                self.logger.warning("Could not read value %s, gave exception %s Using value %d" % (value_desc, ex, value))
        # Yield if we can, allow other time constraint threads to run
        if self.appSocketIO is not None:
            self.appSocketIO.sleep(0.01)
        return value
