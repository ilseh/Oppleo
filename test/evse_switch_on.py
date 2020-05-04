#!/usr/bin/env python
# https://raspberrytips.nl/kaarslicht-pwm-raspberry-pi/

import RPi.GPIO as GPIO

GPIO.setwarnings(False)

switch_pin = 5	# GPIO5 pin 29

GPIO.setmode(GPIO.BCM) # BCM mode

GPIO.setup(switch_pin, GPIO.OUT, initial=GPIO.HIGH)

# Setting the output to LOW enables the charging. Keep low.
GPIO.output(switch_pin, GPIO.LOW)

print(" Done.")

# Don't do cleanup, messes with the output so it doesn't stay low!
#GPIO.cleanup()
