# https://raspberrytips.nl/kaarslicht-pwm-raspberry-pi/

import logging

from .LedLightDev import LedLightDev

from nl.carcharging.utils.GenericUtil import GenericUtil

try:
    from .LedLightProd import LedLightProd
except NameError:
    print('Assuming dev env')

PULSE_LED_MIN = 3
PULSE_LED_MAX = 98


class LedLighter(object):
    LED_RED = 13
    LED_GREEN = 12
    LED_BLUE = 16

    def __init__(self, *colors, services=None):
        self.logger = logging.getLogger('nl.carcharging.services.LedLighter')
        if services is None:
            services = []
        self.services = services
        self.brightness = None

        if GenericUtil.isProd():
            for color in colors:
                self.services.append(LedLightProd(color))
        else:
            for color in colors:
                self.services.append(LedLightDev(color))

        self.logger.debug('Initialize with %d ledlights' % len(self.services))

    def pulse(self, ):
        for service in self.services:
            service.pulse()

    def pulse_stop(self):
        for service in self.services:
            service.pulse_stop()

    def on(self, brightness):
        self.brightness = brightness
        for service in self.services:
            service.on(brightness)

    def off(self):
        for service in self.services:
            service.off()

    def cleanup(self):
        for service in self.services:
            service.cleanup()
