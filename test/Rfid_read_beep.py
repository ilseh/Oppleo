#!/usr/bin/env python

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

import random, time
import RPi.GPIO as GPIO

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

print(color.BOLD + 'Hello World !' + color.END)
buzzer = 16 # PIN GPIO23

GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering


GPIO.setup(buzzer, GPIO.OUT, initial=GPIO.LOW)

reader = SimpleMFRC522()

print("RFID Blocking Read checker (stop using CRTL-C)")
print(" Ignore "+color.BOLD+"AUTH ERROR!!"+color.END+" and "+color.BOLD+"AUTH ERROR(status2reg & 0x08) != 0"+color.END+" messages.")
print(" The ID is read anyway. Use "+color.BOLD+"python3 Rfid_read_beep.py 2> /dev/null"+color.END+" to not show the error output.")
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
