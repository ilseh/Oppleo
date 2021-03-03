import logging

from nl.oppleo.services.LedLightProdHardware import LedLightProdHardware
from nl.oppleo.utils.GenericUtil import GenericUtil

GenericUtil.importGpio()

# Interval in ms to update led light
FREQ_MS_TO_UPDATE_LED = 10


class LedLightProd(object):

    def __init__(self, color, intensity, pwm=None):
        self.logger = logging.getLogger('nl.oppleo.services.LedLightProd')
        self.color = color
        self.hardware = LedLightProdHardware(self.color)
        self.pwm = pwm
        self.intensity = intensity

    def on(self):
        self.logger.debug('Starting led light %s (intensity %d)' % (self.hardware.color_desc(), self.intensity))
        self.pwm = self.hardware.init_gpio_pwm()
        if self.pwm is None:
            self.logger.debug('Led light %s not started (intensity %d)' % (self.hardware.color_desc(), self.intensity))
            return
        try:
            self.pwm.start(0)
            self.logger.debug('Started led light %s (intensity %d)' % (self.hardware.color_desc(), self.intensity))
            self.pwm.ChangeDutyCycle(self.intensity)
        except Exception as ex:
            self.logger.error('Exception lighting led %s' % ex)

    def off(self):
        self.logger.debug('Stopping led light %s (intensity %d)' % (self.hardware.color_desc(), self.intensity))
        if self.pwm is None:
            self.logger.debug('Led light %s not stopped (intensity %d)' % (self.hardware.color_desc(), self.intensity))
            return
        try:
            self.pwm.stop()
        except Exception as ex:
            self.logger.debug("Could not stop pwm, assume not running %s" % ex)


    def cleanup(self):
        self.hardware.cleanup()