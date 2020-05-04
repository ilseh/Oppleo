#!/usr/bin/env python

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

reader = SimpleMFRC522()

print ("ready to read...")

try:
        id, text = reader.read()
        print("ID:", id)
        print("Text:", text)
finally:
        GPIO.cleanup()


