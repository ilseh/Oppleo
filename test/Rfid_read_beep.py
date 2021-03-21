#!/usr/bin/env python

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

import random, time
import RPi.GPIO as GPIO

buzzer = 16 # PIN GPIO23

GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering


GPIO.setup(buzzer, GPIO.OUT, initial=GPIO.LOW)

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

                GPIO.output(buzzer, GPIO.HIGH) # Turn on
                time.sleep(0.05)
                GPIO.output(buzzer, GPIO.LOW) # Turn off
                print(" Sleep 0.8s to prevent re-read...")
                time.sleep(0.8)

        except KeyboardInterrupt:
                run = False

GPIO.cleanup(buzzer)

print("Done.")
