#!/usr/bin/env python
# https://raspberrytips.nl/kaarslicht-pwm-raspberry-pi/

import RPi.GPIO as GPIO

GPIO.setwarnings(False)

switch_pin = 5	# GPIO5 pin 29

GPIO.setmode(GPIO.BCM) # BCM mode

GPIO.setup(switch_pin, GPIO.OUT, initial=GPIO.HIGH)

# Setting the output to HIGH disables the charging. Keep high.
GPIO.output(switch_pin, GPIO.HIGH)

print(" Done.")

# Don't do cleanup, messes with the output so it doesn't stay high!
#GPIO.cleanup()
