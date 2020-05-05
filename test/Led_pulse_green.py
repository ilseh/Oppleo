#!/usr/bin/env python
# https://raspberrytips.nl/kaarslicht-pwm-raspberry-pi/

import random, time
import RPi.GPIO as GPIO

led_red = 13
led_green = 12
led_blue = 16

led = 12

def millis():
   return int(round(time.time() * 1000))

GPIO.setmode(GPIO.BCM)
GPIO.setup(led, GPIO.OUT)

pwm = GPIO.PWM(led, 100)
RUNNING = True

pulseLedValue = 0
pulseLedMillis = 0
pulseLedUp = True
pulseLedDutyCycle = 1  # 1s / 100 steps = 10ms/step
pulseLedMin = 3
pulseLedMax = 98


print ("Stop -> CTRL + C")

try:
   pwm.start(0)
   while RUNNING:
      if (millis() > (pulseLedMillis + ((pulseLedDutyCycle * 1000) / 100))):
         if ((pulseLedUp and (pulseLedValue >= pulseLedMax)) or
             ((not pulseLedUp) and (pulseLedValue <= pulseLedMin))):
            pulseLedUp = not pulseLedUp
         if (pulseLedUp):
            pulseLedValue += 1
         else:
            pulseLedValue -= 1
         pwm.ChangeDutyCycle(pulseLedValue)
         print ("pulseLedValue = ", pulseLedValue)
         pulseLedMillis = millis()

except KeyboardInterrupt:
   running = False

finally:
   pwm.stop()
   GPIO.cleanup()
