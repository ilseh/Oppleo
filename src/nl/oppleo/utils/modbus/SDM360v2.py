# Eastron SDM630-Modbus MID V2, 3 Fase kWh meter met Modbus RS485 100A   € 139


SDM630v2 = { 
        "name"          : "SDM630v2",
        "short"         : "Eastron SDM630v2 3 fase",
        "description"   : "Eastron SDM630-Modbus MID V2, 3 Fase kWh meter met Modbus RS485 100A",

        # read_register(registeraddress, number_of_decimals=0, functioncode=3, signed=False)
        "serialNumber"  : {
            "enabled"   : True,
            "type"      : "register",
            # 40043 Serial Number Hi  00  2A  Read the first product serial number.
            "Hi": {
                "ra"    : 42,   # registeraddress
                "nod"   : 0,    # number_of_decimals
                "fc"    : 3,    # functioncode,
                "s"     : False # signed
            },
            # 40045 Serial Number Lo  00  2C  Read the second product serial number.
            "Lo": {
                "ra"    : 44,   # registeraddress
                "nod"   : 0,    # number_of_decimals
                "fc"    : 3,    # functioncode,
                "s"     : False # signed
            },
        },

        # read_float(registeraddress, functioncode, number_of_registers, byteorder)
        "L1": {
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
            # 30359 Phase 1 total kWh. [kWh]
            "kWh": {
                "enabled"   : True,
                "type"      : "float",
                "ra"        : 358,  # registeraddress
                "fc"        : 4,    # functioncode,
                "nor"       : 2,    # number_of_registers
                "bo"        : 0     # byteorder
            }
        },

    "L2": {
            # 30015 Phase 2 power. [W]
            "P": {
                "enabled"   : True,
                "type"      : "float",
                "ra"        : 14,   # registeraddress
                "fc"        : 4,    # functioncode,
                "nor"       : 2,    # number_of_registers
                "bo"        : 0     # byteorder
            },
            # 30003     0   2  Phase 2 line to neutral volts. [V]
            "V": {
                "enabled"   : True,
                "type"      : "float",
                "ra"        : 2,    # registeraddress
                "fc"        : 4,    # functioncode,
                "nor"       : 2,    # number_of_registers
                "bo"        : 0     # byteorder
            },
            # 30009 Phase 2 current. [A]
            "A": {
                "enabled"   : True,
                "type"      : "float",
                "ra"        : 8,    # registeraddress
                "fc"        : 4,    # functioncode,
                "nor"       : 2,    # number_of_registers
                "bo"        : 0     # byteorder
            },
            # 30361 Phase 2 total kWh. [kWh]
            "kWh": {
                "enabled"   : True,
                "type"      : "float",
                "ra"        : 360,  # registeraddress
                "fc"        : 4,    # functioncode,
                "nor"       : 2,    # number_of_registers
                "bo"        : 0     # byteorder
            }
        },

        "L3": {
            # 30017 Phase 3 power. [W]
            "P": {
                "enabled"   : True,
                "type"      : "float",
                "ra"        : 16,   # registeraddress
                "fc"        : 4,    # functioncode,
                "nor"       : 2,    # number_of_registers
                "bo"        : 0     # byteorder
            },
            # 30005     0   4  Phase 3 line to neutral volts. [V]
            "V": {
                "enabled"   : True,
                "type"      : "float",
                "ra"        : 4,    # registeraddress
                "fc"        : 4,    # functioncode,
                "nor"       : 2,    # number_of_registers
                "bo"        : 0     # byteorder
            },
            # 30011 Phase 3 current. [A]
            "A": {
                "enabled"   : True,
                "type"      : "float",
                "ra"        : 10,   # registeraddress
                "fc"        : 4,    # functioncode,
                "nor"       : 2,    # number_of_registers
                "bo"        : 0     # byteorder
            },
            # 30363 Phase 3 total kWh. [kWh]
            "kWh": {
                "enabled"   : True,
                "type"      : "float",
                "ra"        : 362,  # registeraddress
                "fc"        : 4,    # functioncode,
                "nor"       : 2,    # number_of_registers
                "bo"        : 0     # byteorder
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
