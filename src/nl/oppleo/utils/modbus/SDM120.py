# Eastron SDM120-Modbus MID, 1 Fase kWh meter met Modbus RS485 45A   € 50
import nl.oppleo.utils.modbus.MB as MB

SDM120 = {
        MB.NAME         : "SDM120",
        MB.SHORT        : "Eastron SDM120 1 fase",
        MB.DESC         : "Eastron SDM120-Modbus MID, 1 Fase kWh meter met Modbus RS485 45A",

        # read_register(registeraddress, number_of_decimals=0, functioncode=3, signed=False)
        MB.SN: {
            MB.ENABLED      : False # NOT IMPLEMENTED
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
            MB.ENERGY: {
                MB.ENABLED   : False,
            }
        },

        MB.L2: {
            MB.POWER: {
                MB.ENABLED   : False
            },
            MB.VOLT: {
                MB.ENABLED   : False
            },
            MB.AMP: {
                MB.ENABLED   : False
            },
            MB.ENERGY: {
                MB.ENABLED   : False,
            }
        },

        MB.L3: {
            MB.POWER: {
                MB.ENABLED   : False
            },
            MB.VOLT: {
                MB.ENABLED   : False
            },
            MB.AMP: {
                MB.ENABLED   : False
            },
            MB.ENERGY: {
                MB.ENABLED   : False,
            }
        },

        # 30071 Frequency of supply voltages. [Hz]
        MB.FREQ: {
            MB.ENABLED                  : True,
            MB.TYPE                     : MB.TYPE_FLOAT,
            MB.REGISTER_ADDRESS         : 70,   # registeraddress
            MB.FUNCTION_CODE            : 4,    # functioncode,
            MB.NUMBER_OF_REGISTERS      : 2,    # number_of_registers
            MB.BYTE_ORDER               : 0     # byteorder
        },

        # 30343   1   56   Total kWh. [kWh]
        MB.TOTAL_ENERGY: {
            MB.ENABLED                  : True,
            MB.TYPE                     : MB.TYPE_FLOAT,
            MB.REGISTER_ADDRESS         : 342,  # registeraddress
            MB.FUNCTION_CODE            : 4,    # functioncode,
            MB.NUMBER_OF_REGISTERS      : 2,    # number_of_registers
            MB.BYTE_ORDER               : 0     # byteorder
        }

    }
