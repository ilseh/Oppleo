# https://raspberrytips.nl/kaarslicht-pwm-raspberry-pi/

import os

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
    services = []

    def __init__(self, *colors):
        env_name = os.getenv('CARCHARGING_ENV')
        if self.isProd(env_name):
            for color in colors:
                self.services.append(LedLightProd(color))
        else:
            for color in colors:
                self.services.append(LedLightDev(color))


    def isProd(self, env_name):
        return env_name.lower() == PROD

    def pulse(self,):
        for service in self.services:
            service.pulse()

    def pulse_stop(self):
        for service in self.services:
            service.pulse_stop()

    def on(self, brightness):
        for service in self.services:
            service.on(brightness)

    def off(self):
        for service in self.services:
            service.off()
