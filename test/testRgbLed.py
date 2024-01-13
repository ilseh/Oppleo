import logging
from nl.oppleo.config.OppleoSystemConfig import OppleoSystemConfig
from nl.oppleo.config.OppleoConfig import OppleoConfig
from nl.oppleo.utils.ModulePresence import modulePresence
from nl.oppleo.services.led.RGBLedControllerThread import RGBLedControllerThread

oppleoSystemConfig = OppleoSystemConfig()
oppleoConfig = OppleoConfig()

print("RGB Led simulator")

GPIO = modulePresence.GPIO
# We are the only GPIO user, ignore warnings
GPIO.setwarnings(False)
# Set pin mode to BCM. Normally done in Oppleo.py main file
GPIO.setmode(GPIO.BCM)

oppleoConfig.rgblcThread = RGBLedControllerThread()

print("Starting RGBLedControllerThread...")
oppleoConfig.rgblcThread.start()

run = True
while run:

    try:
        option = input("Please state 'open', 'close', 'charge', 'nocharge', 'error' or 'flash' or 'stop':")
        if option.upper() in ['OPEN', 'CLOSE', 'CHARGE', 'NOCHARGE', 'ERROR', 'NOERROR', 'FLASH', 'STOP']:
            if option.upper() == 'STOP':
                print("Stopping...")
                run = False
            if option.upper() == 'OPEN':
                print("Opening session...")
                oppleoConfig.rgblcThread.openSession = True
            if option.upper() == 'CLOSE':
                if oppleoConfig.rgblcThread.charging:
                    print("Stop charging...")
                    oppleoConfig.rgblcThread.charging = False
                print("Closing session...")
                oppleoConfig.rgblcThread.openSession = False
            if option.upper() == 'CHARGE':
                if not oppleoConfig.rgblcThread.openSession:
                    print("Opening session...")
                    oppleoConfig.rgblcThread.openSession = True
                print("Start charging...")
                oppleoConfig.rgblcThread.charging = True
            if option.upper() == 'NOCHARGE':
                print("Stop charging...")
                oppleoConfig.rgblcThread.charging = False
            if option.upper() == 'ERROR':
                print("Setting error...")
                oppleoConfig.rgblcThread.error = True
            if option.upper() == 'NOERROR':
                print("Clearing error...")
                oppleoConfig.rgblcThread.error = False
            if option.upper() == 'FLASH':
                print("Error flash...")
                oppleoConfig.rgblcThread.errorFlash = True
        else:
            print("Input '{}' not recognized.".format(option))
    except KeyboardInterrupt as kbi:
        # CTRL-C
        print("Stopping...")
        run = False


print("Stopping RGBLedControllerThread...")
oppleoConfig.rgblcThread.stop()

print("Done.")

