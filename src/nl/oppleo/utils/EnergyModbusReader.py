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


class EnergyModbusReader:
    energy_device_id = None
    instrument = None
    appSocketIO = None
    modbusConfig = None
 
    def __init__(self, energy_device_id, appSocketIO=None):
        self.logger = logging.getLogger('nl.oppleo.services.EnergyUtil')
        self.energy_device_id = energy_device_id
        self.appSocketIO = appSocketIO
        self.oppleoConfig = OppleoConfig()
        self.logger.debug('Production environment, calling initInstrument()')
        self.initInstrument()
        self.threadLock = threading.Lock()


    def initInstrument(self):
        global minimalmodbus, SDM630v2, SDM120

        energy_device_data = EnergyDeviceModel.get()
        self.logger.debug(
            'found device: %s %s %d' % (energy_device_data.energy_device_id, energy_device_data.port_name, energy_device_data.slave_address))

        minimalmodbus.TIMEOUT = energy_device_data.modbus_timeout

        try:
            self.instrument = minimalmodbus.Instrument(energy_device_data.port_name,
                                                       energy_device_data.slave_address
                                                      )
        except Exception as e:
            self.logger.error("initInstrument() failed: {}".format(str(e)))
            raise

        # Get this from the database
        self.instrument.serial.baudrate = energy_device_data.baudrate
        self.instrument.serial.bytesize = energy_device_data.bytesize
        self.instrument.serial.parity = energy_device_data.parity
        self.instrument.serial.stopbits = energy_device_data.stopbits
        self.instrument.serial.timeout = energy_device_data.serial_timeout
        self.instrument.debug = energy_device_data.debug
        self.instrument.mode = energy_device_data.mode
        self.instrument.close_port_after_each_call = energy_device_data.close_port_after_each_call

        self.modbusConfig = SDM630v2
        for i in range(len(modbusConfigOptions)): 
            if energy_device_data.modbus_config == modbusConfigOptions[i]['name']:
                self.modbusConfig = modbusConfigOptions[i]
        self.logger.debug("Modbus config {} selected (default: {}).".format(self.modbusConfig['name'], SDM630v2['name']))

        self.readSerialNumber(energy_device_data.port_name, energy_device_data.slave_address)


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
        self.logger.debug('Production environment, getting real data')
        return self.getProdTotalKWHHValue()

    def getMeasurementValue(self):
        self.logger.debug('Production environment, getting real data')
        return self.getProdMeasurementValue()


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
        # self.logger.debug("try_read_float_from_config name:{} el:{}".format(name, str(el)))

        if not el['enabled']:
            self.logger.debug("Modbus element {} not enabled".format(name))
            return 0
        if el['type'] != "float":
            self.logger.warn("Type {} for modbus element {} not supported (must be float)".format(el['type'], name))
            return 0
        return round( self.try_read_float( name, el['ra'], el['fc'], el['nor'], el['bo'] ), 1 )
        

    def getProdMeasurementValue(self):

        L1_P = self.try_read_float_from_config( 'l1_p', self.modbusConfig['L1']['P'] )
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
