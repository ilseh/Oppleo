import minimalmodbus
import threading

from nl.oppleo.config.OppleoConfig import OppleoConfig
from nl.oppleo.models.EnergyDeviceModel import EnergyDeviceModel
import logging

# https://minimalmodbus.readthedocs.io/en/stable/modbusdetails.html
MODBUS_FUNCTION_CODE_DISCRETE = 2
MODBUS_FUNCTION_CODE_HOLDING  = 3
MODBUS_FUNCTION_CODE_INPUT    = 4


import nl.oppleo.utils.modbus.MB as MB
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
        self.logger = logging.getLogger('nl.oppleo.services.EnergyModbusReader')
        self.energy_device_id = energy_device_id
        self.appSocketIO = appSocketIO
        self.oppleoConfig:OppleoConfig = OppleoConfig()
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
            if energy_device_data.modbus_config == modbusConfigOptions[i][MB.NAME]:
                self.modbusConfig = modbusConfigOptions[i]
        self.logger.debug("Modbus config {} selected (default: {}).".format(self.modbusConfig[MB.NAME], SDM630v2[MB.NAME]))

        self.readSerialNumber(energy_device_data.port_name, energy_device_data.slave_address)


    def readSerialNumber(self, port_name=None, slave_address=None):
        self.logger.debug('readSerialNumber()')

        if self.modbusConfig[MB.SN][MB.ENABLED]:
            if self.modbusConfig[MB.SN][MB.TYPE] == MB.TYPE_REGISTER:
                serial_Hi = self.instrument.read_register(  \
                                self.modbusConfig[MB.SN][MB.HI][MB.REGISTER_ADDRESS],  \
                                self.modbusConfig[MB.SN][MB.HI][MB.NUMBER_OF_DECIMALS], \
                                self.modbusConfig[MB.SN][MB.HI][MB.FUNCTION_CODE],  \
                                self.modbusConfig[MB.SN][MB.HI][MB.SIGNED]    \
                                )
                serial_Lo = self.instrument.read_register(  \
                                self.modbusConfig[MB.SN][MB.LO][MB.REGISTER_ADDRESS],  \
                                self.modbusConfig[MB.SN][MB.LO][MB.NUMBER_OF_DECIMALS], \
                                self.modbusConfig[MB.SN][MB.LO][MB.FUNCTION_CODE],  \
                                self.modbusConfig[MB.SN][MB.LO][MB.SIGNED]    \
                                )
                self.logger.debug('readSerialNumber() serial_Hi:{} serial_Lo:{}'.format(serial_Hi, serial_Lo))     
                self.oppleoConfig.kWhMeterSerial = str((serial_Hi * 65536 ) + serial_Lo)
                self.logger.info('kWh meter serial number: {} (port:{}, address:{})'.format(
                        self.oppleoConfig.kWhMeterSerial,
                        port_name,
                        slave_address
                        )
                    )     
            else:
                self.logger.warn('modbusConfig serialNumber type {} not supported!'.format(self.modbusConfig[MB.SN][MB.TYPE]))
                self.oppleoConfig.kWhMeterSerial = 99999999
        else:
            self.oppleoConfig.kWhMeterSerial = 99999999

        return self.oppleoConfig.kWhMeterSerial

 


    def getTotalKWHHValue(self):
        self.logger.debug('Production environment, getting real data')
        return self.getProdTotalKWHHValue()

    def getMeasurementValue(self):
        self.logger.debug('Production environment, getting real data')
        return self.getProdMeasurementValue()


    def getProdTotalKWHHValue(self):
        if self.modbusConfig[MB.TOTAL_ENERGY][MB.TYPE] == MB.TYPE_FLOAT:
            return round(
                self.try_read_float(
                    value_desc='kwh',
                    registeraddress=self.modbusConfig[MB.TOTAL_ENERGY][MB.REGISTER_ADDRESS],
                    functioncode=self.modbusConfig[MB.TOTAL_ENERGY][MB.FUNCTION_CODE],
                    number_of_registers=self.modbusConfig[MB.TOTAL_ENERGY][MB.NUMBER_OF_REGISTERS],
                    byteorder=self.modbusConfig[MB.TOTAL_ENERGY][MB.BYTE_ORDER]
                    ),
                1
                )
        else:
            self.logger.warn('modbusConfig total_kWh type {} not supported!'.format(self.modbusConfig[MB.TOTAL_ENERGY][MB.TYPE]))
            return 0


    def try_read_float_from_config(self, name, el):
        # self.logger.debug("try_read_float_from_config name:{} el:{}".format(name, str(el)))

        if not el[MB.ENABLED]:
            self.logger.debug("Modbus element {} not enabled".format(name))
            return 0
        if el[MB.TYPE] != MB.TYPE_FLOAT:
            self.logger.warn("Type {} for modbus element {} not supported (must be {})".format(el[MB.TYPE], name, MB.TYPE_FLOAT))
            return 0
        return round(self.try_read_float( 
                            value_desc=name, 
                            registeraddress=el[MB.REGISTER_ADDRESS], 
                            functioncode=el[MB.FUNCTION_CODE], 
                            number_of_registers=el[MB.NUMBER_OF_REGISTERS], 
                            byteorder=el[MB.BYTE_ORDER] 
                        ),
                        1 
                    )
        

    def getProdMeasurementValue(self):

        L1_P = self.try_read_float_from_config( 'l1_p', self.modbusConfig[MB.L1][MB.POWER] )
        L1_V = self.try_read_float_from_config( 'l1_v', self.modbusConfig[MB.L1][MB.VOLT] )
        L1_A = self.try_read_float_from_config( 'l1_a', self.modbusConfig[MB.L1][MB.AMP] )
        L1_kWh = self.try_read_float_from_config( 'l1_kWh', self.modbusConfig[MB.L1][MB.ENERGY] )

        L2_P = self.try_read_float_from_config( 'l2_p', self.modbusConfig[MB.L2][MB.POWER] )
        L2_V = self.try_read_float_from_config( 'l2_v', self.modbusConfig[MB.L2][MB.VOLT] )
        L2_A = self.try_read_float_from_config( 'l2_a', self.modbusConfig[MB.L2][MB.AMP] )
        L2_kWh = self.try_read_float_from_config( 'l2_kWh', self.modbusConfig[MB.L2][MB.ENERGY] )

        L3_P = self.try_read_float_from_config( 'l3_p', self.modbusConfig[MB.L3][MB.POWER] )
        L3_V = self.try_read_float_from_config( 'l3_v', self.modbusConfig[MB.L3][MB.VOLT] )
        L3_A = self.try_read_float_from_config( 'l3_a', self.modbusConfig[MB.L3][MB.AMP] )
        L3_kWh = self.try_read_float_from_config( 'l3_kWh', self.modbusConfig[MB.L3][MB.ENERGY] )

        kWh = self.try_read_float_from_config( 'kWh', self.modbusConfig[MB.TOTAL_ENERGY] )
        Hz = self.try_read_float_from_config( 'hz', self.modbusConfig[MB.FREQ] )

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
        value = 0
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
