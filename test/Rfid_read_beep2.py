#!/usr/bin/env python

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

import random, time
import RPi.GPIO as GPIO

buzzer = 23 # PIN 16 for GPIO.BOARD, 23 for GPIO.BCM (GPIO23)

GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BCM) # GPIO.BCM uses GPIO pin numbering, GPIO.BOARD uses physical pin numbering


GPIO.setup(buzzer, GPIO.OUT, initial=GPIO.LOW)

reader = SimpleMFRC522()

print ("ready to read...")

try:
        id, text = reader.read()
        print("ID:", id)
        print("Text:", text)

        GPIO.output(buzzer, GPIO.HIGH) # Turn on
        time.sleep(0.05)
        GPIO.output(buzzer, GPIO.LOW) # Turn off

finally:
        GPIO.cleanup()


