import logging
import threading

from nl.oppleo.utils.ModulePresence import modulePresence
from nl.oppleo.services.LedPinDefinition import LedPinDefinition


class LedLightProdHardware(object):
    __logger = None
    __ = None
    __pinDefinition:LedPinDefinition = 0

    def __init__(self, pinDefinition:LedPinDefinition):
        self.__logger = logging.getLogger('nl.oppleo.services.LedLightProdHardware')
        # TODO: check if this lock mechanism is still necessary.
        self.__ = threading.Lock()
        self.__pinDefinition = pinDefinition
        self.__logger.debug("LedLightProdHardware.init() pin:{} color:{}".format(str(pinDefinition.pin), pinDefinition.color))
        

    def init_gpio_pwm(self):
        self.__logger.debug("LedLightProdHardware.init_gpio_pwm() for pin:{} color:{}".format(str(self.__pinDefinition.pin), self.__pinDefinition.color))

        with self.__:

            pwm = None

            if not modulePresence.gpioAvailable():
                self.__logger.warn("init_gpio_pwm() - Oppleo LED is enabled but GPIO is not loaded (config error).")
                return None

            GPIO = modulePresence.GPIO
            for i in range(2):
                try:
                    GPIO.setup(self.__pinDefinition.pin, GPIO.OUT)
                    pwm = GPIO.PWM(self.__pinDefinition.pin, 100)
                except Exception as e:
                    self.__logger.warning("init_gpio_pwm() - Could not initialize GPIO {}, retrying".format(str(e)))
                if pwm is not None:
                    self.__logger.debug('init_gpio_pwm() - pwm initialized')
                    break

            return pwm


    def cleanup(self):
        self.__logger.debug("LedLightProdHardware.cleanup() for pin:{} color:{}".format(str(self.__pinDefinition.pin), self.__pinDefinition.color))

        if not modulePresence.gpioAvailable():
            self.__logger.warn("cleanup() - No GPIO, nothing to cleanup.")
            return None

        # Plain Cleanup resets all ports, also for other still running processes, so don't do that!
        # GPIO.cleanup()

        # TODO
        # this cleanup screws up all other settings for this pin
        modulePresence.GPIO.cleanup(self.__pinDefinition.pin)
