# https://raspberrytips.nl/kaarslicht-pwm-raspberry-pi/

import logging
import time
import os
import threading

try:
    from . import LedLightProd
except NameError:
    print('Assuming dev env')


# TODO: move logic for determining env to reusable position
PROD = 'production'



PULSE_LED_MIN = 3
PULSE_LED_MAX = 98

PULSE_LED_DUTY_CYCLE = 1  # 1s / 100 steps = 10ms/step

class LedLigthDev(object):
    logger = logging.getLogger('nl.carcharging.services.LedLighter')
    running = False

    def __init__(self, color):
        self.color = color

    def _fakePulse(self):
        t = threading.currentThread()
        while getattr(t, "do_run", True):
            self.logger.debug('fake pulsing %d' % self.color)


    def pulse(self):
        self.t = threading.Thread(target=self._fakePulse)
        self.t.start()
        self.logger.debug('Fake pulse started in thread')


    def stop(self):
        self.t.do_run = False
        self.t.join()
        self.logger.debug('Fake pulse stopped')


class LedLighter(object):
    LED_RED = 13
    LED_GREEN = 12
    LED_BLUE = 16

    def __init__(self, color):
        self.env_name = os.getenv('CARCHARGING_ENV')
        if self.isProd():
            self.service = LedLightProd(color)
        else:
            self.service = LedLigthDev(color)


    def isProd(self):
        return self.env_name.lower() == PROD

    def pulse(self,):
        self.service.pulse()

    def stop(self):
        self.service.stop()


