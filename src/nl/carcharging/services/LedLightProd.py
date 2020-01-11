import logging

from nl.carcharging.services.LedLightProdHardware import LedLightProdHardware

try:
    import RPi.GPIO as GPIO
except RuntimeError:
    logging.debug('Assuming dev env')


# Interval in ms to update led light
FREQ_MS_TO_UPDATE_LED = 10


class LedLightProd(object):

    def __init__(self, color, pwm=None):
        self.logger = logging.getLogger('nl.carcharging.services.LedLightProd')
        self.color = color
        self.hardware = LedLightProdHardware(self.color)
        self.pwm = pwm

    def on(self, brightness):
        self.pwm = self.hardware.init_gpio_pwm()

        try:
            self.pwm.start(0)
            self.logger.debug('Starting led light %s brightness %d' % (self.hardware.color_desc(), brightness))
            self.pwm.ChangeDutyCycle(brightness)
        except Exception as ex:
            self.logger.error('Exception lighting led %s' % ex)

    def off(self):
        self.logger.debug('Stopping led light %s' % self.hardware.color_desc())
        try:
            self.pwm.stop()
        except Exception as ex:
            self.logger.debug("Could not stop pwm, assume not running %s" % ex)


    def cleanup(self):
        self.hardware.cleanup()