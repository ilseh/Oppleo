#!/usr/bin/env python
# https://raspberrytips.nl/kaarslicht-pwm-raspberry-pi/

import random, time
import RPi.GPIO as GPIO

buzzer = 23 # PIN 16/ GPIO23

GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BCM) # Use physical pin numbering


GPIO.setup(buzzer, GPIO.OUT, initial=GPIO.LOW)

GPIO.output(buzzer, GPIO.HIGH) # Turn on
time.sleep(0.05)
GPIO.output(buzzer, GPIO.LOW) # Turn off
time.sleep(1) # Sleep for 1 second

GPIO.output(buzzer, GPIO.HIGH) # Turn on
time.sleep(0.1)
GPIO.output(buzzer, GPIO.LOW) # Turn off
time.sleep(0.05) 
GPIO.output(buzzer, GPIO.HIGH) # Turn on
time.sleep(0.1)
GPIO.output(buzzer, GPIO.LOW) # Turn off

time.sleep(1) 

GPIO.output(buzzer, GPIO.HIGH) # Turn on
time.sleep(0.05)
GPIO.output(buzzer, GPIO.LOW) # Turn off
time.sleep(0.05)
GPIO.output(buzzer, GPIO.HIGH) # Turn on
time.sleep(0.05)
GPIO.output(buzzer, GPIO.LOW) # Turn off

GPIO.cleanup()
