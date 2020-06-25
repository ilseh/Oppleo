# Eastron SDM120-Modbus MID, 1 Fase kWh meter met Modbus RS485 45A   € 50

SDM120 = {
        "name"          : "SDM120",
        "short"         : "Eastron SDM120 1 fase",
        "description"   : "Eastron SDM120-Modbus MID, 1 Fase kWh meter met Modbus RS485 45A",

        # read_register(registeraddress, number_of_decimals=0, functioncode=3, signed=False)
        "serialNumber"  : {
            "enabled"   : False # NOT IMPLEMENTED
        },

        # read_float(registeraddress, functioncode, number_of_registers, byteorder)
        "L1"            : {
            # 30013 Phase 1 power. [W]
            "P": {
                "enabled"   : True,
                "type"      : "float",
                "ra"        : 12,   # registeraddress
                "fc"        : 4,    # functioncode,
                "nor"       : 2,    # number_of_registers
                "bo"        : 0     # byteorder
            },
            # 30001     0   0  Phase 1 line to neutral volts. [V]
            "V": {
                "enabled"   : True,
                "type"      : "float",
                "ra"        : 0,    # registeraddress
                "fc"        : 4,    # functioncode,
                "nor"       : 2,    # number_of_registers
                "bo"        : 0     # byteorder
            },
            # 30007 Phase 1 current. [A]
            "A": {
                "enabled"   : True,
                "type"      : "float",
                "ra"        : 6,    # registeraddress
                "fc"        : 4,    # functioncode,
                "nor"       : 2,    # number_of_registers
                "bo"        : 0     # byteorder
            },
            "kWh": {
                "enabled"   : False,
            }
        },

        "L2": {
            "P": {
                "enabled"   : False
            },
            "V": {
                "enabled"   : False
            },
            "A": {
                "enabled"   : False
            },
            "kWh": {
                "enabled"   : False,
            }
        },

        "L3": {
            "P": {
                "enabled"   : False
            },
            "V": {
                "enabled"   : False
            },
            "A": {
                "enabled"   : False
            },
            "kWh": {
                "enabled"   : False,
            }
        },

        # 30071 Frequency of supply voltages. [Hz]
        "Hz": {
            "enabled"   : True,
            "type"      : "float",
            "ra"        : 70,   # registeraddress
            "fc"        : 4,    # functioncode,
            "nor"       : 2,    # number_of_registers
            "bo"        : 0     # byteorder
        },

        # 30343   1   56   Total kWh. [kWh]
        "total_kWh": {
            "enabled"   : True,
            "type"      : "float",
            "ra"        : 342,  # registeraddress
            "fc"        : 4,    # functioncode,
            "nor"       : 2,    # number_of_registers
            "bo"        : 0     # byteorder
        }

    }
