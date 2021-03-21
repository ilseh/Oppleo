#!/usr/bin/env python

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

import random, time

buzzer = 23 # PIN 16 for GPIO.BOARD, 23 for GPIO.BCM (GPIO23)

GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BCM) # GPIO.BCM uses GPIO pin numbering, GPIO.BOARD uses physical pin numbering


GPIO.setup(buzzer, GPIO.OUT, initial=GPIO.LOW)

reader = SimpleMFRC522()

print ("RFID Non-Blocking Read checker (stop using CRTL-C)")
cnt = 0

# SimpleMFRC522() read() blocks other threads, call read_no_block() instead to yield to other threads.
run = True
while run:
        cnt = cnt +1
        try:
                print (" calling SimpleMFRC522().read_no_block() [{}]".format(cnt))
                # This call returns every time, with id is None when no rfid tag was detected
                id, text = reader.read_no_block()
                if id is not None:
                        print("  ID:", id)
                        print("  Text:", text)
                        GPIO.output(buzzer, GPIO.HIGH) # Turn on
                        time.sleep(0.05)
                        GPIO.output(buzzer, GPIO.LOW) # Turn off
                        time.sleep(0.8)
                time.sleep(0.05)
            
        except KeyboardInterrupt:
                run = False

GPIO.cleanup(buzzer)

print("Done.")
