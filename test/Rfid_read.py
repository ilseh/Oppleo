#!/usr/bin/env python

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

import random, time
import RPi.GPIO as GPIO

GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering


reader = SimpleMFRC522()

print ("RFID Blocking Read checker (stop using CRTL-C)")
cnt = 0

run = True
while run:
        cnt = cnt +1
        try:
                print (" calling SimpleMFRC522().read() [{}]".format(cnt))
                id, text = reader.read()
                print("  ID:", id)
                print("  Text:", text)
                print(" Sleep 0.8s to prevent re-read...")
                time.sleep(0.8)

        except KeyboardInterrupt:
                run = False

print("Done.")
