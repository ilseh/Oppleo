#!/usr/bin/python
import threading
import time
import subprocess

# The interface
import minimalmodbus

from minimalmodbus import NoResponseError
from minimalmodbus import ModbusException
from time import sleep

# All data values in the SDM630Modbus smart meter are transferred as 32 bit IEEE754 floating point numbers, (input and output) 
# therefore each SDM630Modbus meter value is transferred using two Modbus Protocol registers. All register read requests and 
# data write requests must specify an even number of registers. Attempts to read/write an odd number of registers prompt
# the SDM630Modbus smart meter to return a Modbus Protocol exception message. However, for compatibility with some SCADA systems, 
# SDM630Modbus Smart meter will response to any single input or holding register read with an instrument type specific value.

instrument = minimalmodbus.Instrument('/dev/ttyUSB0', 1)  # port name, slave address (in decimal)
#instrument = minimalmodbus.Instrument('/dev/ttyUSB1', 1)  # port name, slave address (in decimal)

#instrument.close_port_after_each_call = True
instrument.close_port_after_each_call = False

#instrument.serial.baudrate = 9600
instrument.serial.baudrate = 38400
instrument.serial.bytesize = 8
instrument.serial.parity = minimalmodbus.serial.PARITY_NONE
instrument.serial.stopbits = 1
instrument.serial.timeout = 1
instrument.debug = False
instrument.mode = minimalmodbus.MODE_RTU

#print(instrument)

def read_SDM630V2_meter():
  # read_float(registeraddress, functioncode=3, number_of_registers=2, byteorder=0)

  try:
    L1_V = round( instrument.read_float(0, 4, 2, 0), 1)   # 30001 Phase 1 line to neutral volts. [V]
    L2_V = round( instrument.read_float(2, 4, 2, 0), 1)   # 30003 Phase 2 line to neutral volts. [V]
    L3_V = round( instrument.read_float(4, 4, 2, 0), 1)   # 30005 Phase 3 line to neutral volts. [V]

    L1_A = round( instrument.read_float(6, 4, 2, 0), 1)   # 30007 Phase 1 current. [A]
    L2_A = round( instrument.read_float(8, 4, 2, 0), 1)   # 30009 Phase 2 current. [A]
    L3_A = round( instrument.read_float(10, 4, 2, 0), 1)  # 30011 Phase 3 current. [A]

    L1_P = round( instrument.read_float(12, 4, 2, 0), 1)   # 30013 Phase 1 power. [W]
    L2_P = round( instrument.read_float(14, 4, 2, 0), 1)   # 30013 Phase 2 power. [W]
    L3_P = round( instrument.read_float(16, 4, 2, 0), 1)   # 30013 Phase 3 power. [W]

    L1_kWh = round( instrument.read_float(358, 4, 2, 0), 1)   # 300359 Phase 1 total kWh. [kWh]
    L2_kWh = round( instrument.read_float(360, 4, 2, 0), 1)   # 300361 Phase 2 total kWh. [kWh]
    L3_kWh = round( instrument.read_float(362, 4, 2, 0), 1)   # 300363 Phase 3 total kWh. [kWh]

    kWh = round( instrument.read_float(342, 4, 2, 0), 1)   # 300343 Total kWh. [kWh]

    HZ = round( instrument.read_float(70, 4, 2, 0), 1)    # 30071 Frequency of supply voltages. [Hz]

    print("%s L1:%1.1fV/%1.1fA/%1.1fW/%1.1fkWh L2:%1.1fV/%1.1fA/%1.1fW/%1.1fkWh L3:%1.1fV/%1.1fA/%1.1fW/%1.1fkWh %1.1fHz %1.1fkWh" % (time.strftime('%Y%m%d %X ->'), L1_V, L1_A, L1_P, L1_kWh, L2_V, L2_A, L2_P, L2_kWh, L3_V, L3_A, L3_P, L3_kWh, HZ, kWh))
  except NoResponseError as e:
    print("No communication with the instrument (no answer)")
  except TypeError as e:
    # Errors related to wrong argument to functions raises TypeError or ValueError. 
    print(e, False)
  except ValueError as e:
    # Errors related to wrong argument to functions raises TypeError or ValueError.
    print(e, False)
  except ModbusException as e:
    # When there is communication problems etc the exceptions raised are ModbusException (with subclasses) and 
    # serial.serialutil.SerialException, which both are inheriting from IOError.
    # Note that in Python3 the IOError is an alias for OSError.
    print(e, False)
  except Exception as e:
    # Output unexpected Exceptions.
    print(e, False)


print("Ready to read SDM630V2 100A MODBUS...")

RUNNING = True

try:
   while RUNNING:
      now = time.time() *1000.0
      read_SDM630V2_meter()
      delta = (time.time() *1000) - now
      print(" Reading values took {}ms".format(round(delta*10)/10))
      time.sleep(5) # 3 seconds

except KeyboardInterrupt:
   RUNNING = False

finally:
   print("Done")

