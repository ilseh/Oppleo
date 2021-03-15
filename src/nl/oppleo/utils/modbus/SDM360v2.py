# Eastron SDM630-Modbus MID V2, 3 Fase kWh meter met Modbus RS485 100A   € 139
import nl.oppleo.utils.modbus.MB as MB

SDM630v2 = { 
        MB.NAME          : "SDM630v2",
        MB.SHORT         : "Eastron SDM630v2 3 fase",
        MB.DESC          : "Eastron SDM630-Modbus MID V2, 3 Fase kWh meter met Modbus RS485 100A",

        # read_register(registeraddress, number_of_decimals=0, functioncode=3, signed=False)
        MB.SN: {
            MB.ENABLED   : True,
            MB.TYPE      : MB.TYPE_REGISTER,
            # 40043 Serial Number Hi  00  2A  Read the first product serial number.
            MB.HI: {
                MB.REGISTER_ADDRESS     : 42,   # registeraddress
                MB.NUMBER_OF_DECIMALS   : 0,    # number_of_decimals
                MB.FUNCTION_CODE        : 3,    # functioncode,
                MB.SIGNED               : False # signed
            },
            # 40045 Serial Number Lo  00  2C  Read the second product serial number.
            MB.LO: {
                MB.REGISTER_ADDRESS     : 44,   # registeraddress
                MB.NUMBER_OF_DECIMALS   : 0,    # number_of_decimals
                MB.FUNCTION_CODE        : 3,    # functioncode,
                MB.SIGNED               : False # signed
            },
        },

        # read_float(registeraddress, functioncode, number_of_registers, byteorder)
        MB.L1: {
            # 30013 Phase 1 power. [W]
            MB.POWER: {
                MB.ENABLED              : True,
                MB.TYPE                 : MB.TYPE_FLOAT,
                MB.REGISTER_ADDRESS     : 12,   # registeraddress
                MB.FUNCTION_CODE        : 4,    # functioncode,
                MB.NUMBER_OF_REGISTERS  : 2,    # number_of_registers
                MB.BYTE_ORDER           : 0     # byteorder
            },
            # 30001     0   0  Phase 1 line to neutral volts. [V]
            MB.VOLT: {
                MB.ENABLED              : True,
                MB.TYPE                 : MB.TYPE_FLOAT,
                MB.REGISTER_ADDRESS     : 0,    # registeraddress
                MB.FUNCTION_CODE        : 4,    # functioncode,
                MB.NUMBER_OF_REGISTERS  : 2,    # number_of_registers
                MB.BYTE_ORDER           : 0     # byteorder
            },
            # 30007 Phase 1 current. [A]
            MB.AMP: {
                MB.ENABLED              : True,
                MB.TYPE                 : MB.TYPE_FLOAT,
                MB.REGISTER_ADDRESS     : 6,    # registeraddress
                MB.FUNCTION_CODE        : 4,    # functioncode,
                MB.NUMBER_OF_REGISTERS  : 2,    # number_of_registers
                MB.BYTE_ORDER           : 0     # byteorder
            },
            # 30359 Phase 1 total kWh. [kWh]
            MB.ENERGY: {
                MB.ENABLED              : True,
                MB.TYPE                 : MB.TYPE_FLOAT,
                MB.REGISTER_ADDRESS     : 358,  # registeraddress
                MB.FUNCTION_CODE        : 4,    # functioncode,
                MB.NUMBER_OF_REGISTERS  : 2,    # number_of_registers
                MB.BYTE_ORDER           : 0     # byteorder
            }
        },

        MB.L2: {
            # 30015 Phase 2 power. [W]
            MB.POWER: {
                MB.ENABLED              : True,
                MB.TYPE                 : MB.TYPE_FLOAT,
                MB.REGISTER_ADDRESS     : 14,   # registeraddress
                MB.FUNCTION_CODE        : 4,    # functioncode,
                MB.NUMBER_OF_REGISTERS  : 2,    # number_of_registers
                MB.BYTE_ORDER           : 0     # byteorder
            },
            # 30003     0   2  Phase 2 line to neutral volts. [V]
            MB.VOLT: {
                MB.ENABLED              : True,
                MB.TYPE                 : MB.TYPE_FLOAT,
                MB.REGISTER_ADDRESS     : 2,    # registeraddress
                MB.FUNCTION_CODE        : 4,    # functioncode,
                MB.NUMBER_OF_REGISTERS  : 2,    # number_of_registers
                MB.BYTE_ORDER           : 0     # byteorder
            },
            # 30009 Phase 2 current. [A]
            MB.AMP: {
                MB.ENABLED              : True,
                MB.TYPE                 : MB.TYPE_FLOAT,
                MB.REGISTER_ADDRESS     : 8,    # registeraddress
                MB.FUNCTION_CODE        : 4,    # functioncode,
                MB.NUMBER_OF_REGISTERS  : 2,    # number_of_registers
                MB.BYTE_ORDER           : 0     # byteorder
            },
            # 30361 Phase 2 total kWh. [kWh]
            MB.ENERGY: {
                MB.ENABLED              : True,
                MB.TYPE                 : MB.TYPE_FLOAT,
                MB.REGISTER_ADDRESS     : 360,  # registeraddress
                MB.FUNCTION_CODE        : 4,    # functioncode,
                MB.NUMBER_OF_REGISTERS  : 2,    # number_of_registers
                MB.BYTE_ORDER           : 0     # byteorder
            }
        },

        MB.L3: {
            # 30017 Phase 3 power. [W]
            MB.POWER: {
                MB.ENABLED              : True,
                MB.TYPE                 : MB.TYPE_FLOAT,
                MB.REGISTER_ADDRESS     : 16,   # registeraddress
                MB.FUNCTION_CODE        : 4,    # functioncode,
                MB.NUMBER_OF_REGISTERS  : 2,    # number_of_registers
                MB.BYTE_ORDER           : 0     # byteorder
            },
            # 30005     0   4  Phase 3 line to neutral volts. [V]
            MB.VOLT: {
                MB.ENABLED              : True,
                MB.TYPE                 : MB.TYPE_FLOAT,
                MB.REGISTER_ADDRESS     : 4,    # registeraddress
                MB.FUNCTION_CODE        : 4,    # functioncode,
                MB.NUMBER_OF_REGISTERS  : 2,    # number_of_registers
                MB.BYTE_ORDER           : 0     # byteorder
            },
            # 30011 Phase 3 current. [A]
            MB.AMP: {
                MB.ENABLED              : True,
                MB.TYPE                 : MB.TYPE_FLOAT,
                MB.REGISTER_ADDRESS     : 10,   # registeraddress
                MB.FUNCTION_CODE        : 4,    # functioncode,
                MB.NUMBER_OF_REGISTERS  : 2,    # number_of_registers
                MB.BYTE_ORDER           : 0     # byteorder
            },
            # 30363 Phase 3 total kWh. [kWh]
            MB.ENERGY: {
                MB.ENABLED              : True,
                MB.TYPE                 : MB.TYPE_FLOAT,
                MB.REGISTER_ADDRESS     : 362,  # registeraddress
                MB.FUNCTION_CODE        : 4,    # functioncode,
                MB.NUMBER_OF_REGISTERS  : 2,    # number_of_registers
                MB.BYTE_ORDER           : 0     # byteorder
            }
        },

        # 30071 Frequency of supply voltages. [Hz]
        MB.FREQ: {
            MB.ENABLED              : True,
            MB.TYPE                 : MB.TYPE_FLOAT,
            MB.REGISTER_ADDRESS     : 70,   # registeraddress
            MB.FUNCTION_CODE        : 4,    # functioncode,
            MB.NUMBER_OF_REGISTERS  : 2,    # number_of_registers
            MB.BYTE_ORDER           : 0     # byteorder
        },

        # 30343   1   56   Total kWh. [kWh]
        MB.TOTAL_ENERGY: {
            MB.ENABLED              : True,
            MB.TYPE                 : MB.TYPE_FLOAT,
            MB.REGISTER_ADDRESS     : 342,  # registeraddress
            MB.FUNCTION_CODE        : 4,    # functioncode,
            MB.NUMBER_OF_REGISTERS  : 2,    # number_of_registers
            MB.BYTE_ORDER           : 0     # byteorder
        }
    }
