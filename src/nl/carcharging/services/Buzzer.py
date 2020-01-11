import time
import logging

from nl.carcharging.utils.GenericUtil import GenericUtil

try:
    import RPi.GPIO as GPIO
except RuntimeError:
    logging.debug('Assuming dev env')

buzzer = 23 # PIN 16/ GPIO23


class BuzzerDev(object):

    def __init__(self):
        self.logger = logging.getLogger('nl.carcharging.services.BuzzerDev')

    def buzz(self, buzz_duration_s, iterations=1):
        for i in range(iterations):
            self.logger.debug("Fake buzzzzzzzz!!!!!!!")
            time.sleep(buzz_duration_s)

    def cleanup(self):
        self.logger.debug("Fake cleanup")


class BuzzerProd(object):
    # GPIO.setwarnings(False) # Ignore warning for now
    GPIO.setmode(GPIO.BCM) # Use physical pin numbering


    def __init__(self):
        self.logger = logging.getLogger('nl.carcharging.services.BuzzerProd')

    def buzz(self, buzz_duration_s, iterations=1):
        self.logger.debug("Buzzing. Iteration %d, duration %d" % (iterations, buzz_duration_s))

        GPIO.setup(buzzer, GPIO.OUT, initial=GPIO.LOW)

        for i in range(iterations):
            GPIO.output(buzzer, GPIO.HIGH)  # Turn on
            time.sleep(buzz_duration_s)
            GPIO.output(buzzer, GPIO.LOW)  # Turn off
            time.sleep(.5)

    def cleanup(self):
        GPIO.cleanup()
        self.logger.debug("GPIO cleanup done for %s" % self.color_desc())


class Buzzer(object):

    def __init__(self):
        self.logger = logging.getLogger('nl.carcharging.services.Buzzer')

        if GenericUtil.isProd():
            self.buzzer = BuzzerProd()
        else:
            self.buzzer = BuzzerDev()

    def buzz(self, buzz_duration_s, iterations=1):
        self.buzzer.buzz(buzz_duration_s, iterations)

    def cleanup(self):
        self.buzzer.cleanup()
