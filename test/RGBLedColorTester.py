#!/usr/bin/env python
# https://raspberrytips.nl/kaarslicht-pwm-raspberry-pi/

import random, time
import RPi.GPIO as GPIO

print("RGB Led Color tester")
led_red = 16
led_green = 12
led_blue = 13

GPIO.setmode(GPIO.BCM)
GPIO.setup(led_red, GPIO.OUT, initial=GPIO.LOW))
GPIO.setup(led_green, GPIO.OUT, initial=GPIO.LOW))
GPIO.setup(led_blue, GPIO.OUT, initial=GPIO.LOW))

pwm_red = GPIO.PWM(led_red, 100)
pwm_green = GPIO.PWM(led_green, 100)
pwm_blue = GPIO.PWM(led_blue, 100)

brightness_red = 0
brightness_green = 0
brightness_blue = 0

pwm_red.start(brightness_red)
pwm_green.start(brightness_green)
pwm_blue.start(brightness_blue)

run = True
while run:
   try:
      print("Current RGB brightness R:{} G:{} B:{}".format(brightness_red,brightness_green,brightness_blue))
      color = input("Color? [red/green/blue]")
      if color.upper() in ['R', 'RED', 'G', 'GREEN', 'B', 'BLUE']:
         brightnessInput = input("Brightness? [0-100]")
         brightness = float(brightnessInput)
         if color.upper() in ['R', 'RED']:
            brightness_red = brightness
            pwm_red.ChangeDutyCycle(brightness_red)
         if color.upper() in ['G', 'GREEN']:
            brightness_green = brightness
            pwm_green.ChangeDutyCycle(brightness_green)
         if color.upper() in ['B', 'BLUE']:
            brightness_blue = brightness
            pwm_blue.ChangeDutyCycle(brightness_blue)
            
      pwm_red.start(0)

   except KeyboardInterrupt:
      run = False

pwm_red.stop()
pwm_green.stop()
pwm_blue.stop()
GPIO.cleanup([led_red, led_green, led_blue])

print("Last RGB brightness was R:{} G:{} B:{}".format(brightness_red,brightness_green,brightness_blue))

print("Done.")