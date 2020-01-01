# https://raspberrytips.nl/kaarslicht-pwm-raspberry-pi/

import logging
import time
import os
import threading

from .LedLightDev import LedLightDev

try:
    from .LedLightProd import LedLightProd
except NameError:
    print('Assuming dev env')


# TODO: move logic for determining env to reusable position
PROD = 'production'



PULSE_LED_MIN = 3
PULSE_LED_MAX = 98

PULSE_LED_DUTY_CYCLE = 1  # 1s / 100 steps = 10ms/step




class LedLighter(object):
    LED_RED = 13
    LED_GREEN = 12
    LED_BLUE = 16

    def __init__(self, color):
        self.env_name = os.getenv('CARCHARGING_ENV')
        if self.isProd():
            self.service = LedLightProd(color)
        else:
            self.service = LedLightDev(color)


    def isProd(self):
        return self.env_name.lower() == PROD

    def pulse(self,):
        self.service.pulse()

    def stop(self):
        self.service.stop()


