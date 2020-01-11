# https://raspberrytips.nl/kaarslicht-pwm-raspberry-pi/

import logging

from .LedLightDev import LedLightDev

from nl.carcharging.utils.GenericUtil import GenericUtil
from .LedLightPulseProd import LedLightPulseProd

try:
    from .LedLightProd import LedLightProd
except NameError:
    print('Assuming dev env')

PULSE_LED_MIN = 3
PULSE_LED_MAX = 98


class LedLight(object):
    LED_RED = 13
    LED_GREEN = 12
    LED_BLUE = 16

    def __init__(self, *colors, pulse=False, services=None):
        self.logger = logging.getLogger('nl.carcharging.services.LedLight')
        if services is None:
            services = []
        self.services = services
        self.brightness = None

        for color in colors:
            if GenericUtil.isProd():
                self.services.append(LedLightPulseProd(color) if pulse else LedLightProd(color))
            else:
                self.services.append(LedLightDev(color))

        self.logger.debug('Initialize with %d ledlights %s' % (len(self.services), "to pulse" if pulse else ""))

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
