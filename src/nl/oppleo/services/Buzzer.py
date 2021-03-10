import threading
import time
import logging

from nl.oppleo.config.OppleoSystemConfig import OppleoSystemConfig
from nl.oppleo.config.OppleoConfig import OppleoConfig
from nl.oppleo.utils.ModulePresence import ModulePresence

oppleoSystemConfig = OppleoSystemConfig()
oppleoConfig = OppleoConfig()
modulePresence = ModulePresence()


class BuzzerDev(object):

    def __init__(self):
        self.logger = logging.getLogger('nl.oppleo.services.BuzzerDev')

    def buzz(self, buzz_duration_s, iterations=1):
        for i in range(iterations):
            self.logger.debug("Fake buzzzzzzzz!!!!!!!")
            time.sleep(buzz_duration_s)

    def buzz_other_thread(self, buzz_duration_s, iterations=1):
        self.logger.debug("Starting buzzer in fake other thread")

    def cleanup(self):
        self.logger.debug("Fake cleanup")


class BuzzerProd(object):
    logger = logging.getLogger('nl.oppleo.services.BuzzerProd')

    def buzz(self, buzz_duration_s, iterations=1):
        global oppleoConfig

        self.logger.debug("BuzzerProd - Buzzing. Iteration %d, duration %.2f" % (iterations, buzz_duration_s))

        if not modulePresence.gpioAvailable():
            self.logger.debug("BuzzerProd - Buzz - no GPIO module")
            return

        GPIO = modulePresence.GPIO
        GPIO.setup(oppleoConfig.pinBuzzer, GPIO.OUT, initial=GPIO.LOW)

        for i in range(iterations):
            GPIO.output(oppleoConfig.pinBuzzer, GPIO.HIGH)  # Turn on
            time.sleep(buzz_duration_s)
            GPIO.output(oppleoConfig.pinBuzzer, GPIO.LOW)  # Turn off
            time.sleep(.05)

    def cleanup(self):
        global oppleoConfig

        if not modulePresence.gpioAvailable():
            self.logger.debug("BuzzerProd - cleanup - no GPIO module")
            return
        GPIO = modulePresence.GPIO
        GPIO.output(oppleoConfig.pinBuzzer, GPIO.LOW)  # Turn off
        self.logger.debug("GPIO cleanup done for {}")


    def buzz_other_thread(self, buzz_duration_s, iterations=1):
        self.logger.debug("Starting buzzer in other thread")
        thread_for_pulse = threading.Thread(target=self.buzz, name="BuzzerThread", args=(buzz_duration_s, iterations))
        thread_for_pulse.start()


class Buzzer(object):

    def __init__(self):
        self.logger = logging.getLogger('nl.oppleo.services.Buzzer')

        if oppleoSystemConfig.buzzerEnabled:
            self.buzzer = BuzzerProd()
        else:
            self.buzzer = BuzzerDev()

    def buzz(self, buzz_duration_s, iterations=1):
        self.buzzer.buzz(buzz_duration_s, iterations)

    def buzz_other_thread(self, buzz_duration_s, iterations=1):
        self.buzzer.buzz_other_thread(buzz_duration_s, iterations)

    def cleanup(self):
        self.buzzer.cleanup()
