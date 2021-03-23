#!/usr/bin/env python
# https://raspberrytips.nl/kaarslicht-pwm-raspberry-pi/

import random, time
import RPi.GPIO as GPIO

led_red = 16
led_green = 12
led_blue = 13

led = 16

GPIO.setmode(GPIO.BCM)
GPIO.setup(led, GPIO.OUT)

pwm = GPIO.PWM(led, 100)
RUNNING = True

def brightness():
   return random.randint(5, 100)

def flicker():
   return random.random() / 8

print ("Stop -> CTRL + C")

try:
   while RUNNING:
      pwm.start(0)
      pwm.ChangeDutyCycle(brightness())
      time.sleep(flicker())

except KeyboardInterrupt:
   running = False

finally:
   pwm.stop()
   GPIO.cleanup(led)
