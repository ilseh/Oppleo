import time
import pigpio
import RPi.GPIO as GPIO

# print("Setting GPIO MODE to BOARD")
# GPIO.setmode(GPIO.BOARD)
print("Setting GPIO MODE to BCM")
GPIO.setmode(GPIO.BCM)

# Your hardware config
BUZZER_PIN = 23
LED_RED_PIN = 13
LED_GREEN_PIN = 12
LED_BLUE_PIN = 16
EVSE_OUT = 5
EVSE_IN = 6

SAMPLE_TIME = 0.05  # .05 sec

pi = pigpio.pi()

def _cbf(pin, level, tick):
    print("pin={pin} level={level} tick={}".format(pin=pin, level=level, tick=tick))

_cb = pi.callback(EVSE_IN, pigpio.EITHER_EDGE, _cbf)

print('Init EvseReader done')

print("Enabling EVSE...")
# GPIO.setmode(GPIO.BCM) # Use physical pin numbering
GPIO.setup(EVSE_OUT, GPIO.OUT, initial=GPIO.HIGH)


try:
    while True:

        time.sleep(SAMPLE_TIME)

except KeyboardInterrupt as kbi:
    print("Stopped")
    pass


print("Disabling EVSE...")
# Off is push high
GPIO.output(EVSE_OUT, GPIO.HIGH)

print("Resetting GPIO I/O...")
GPIO.cleanup()

print("Done")
