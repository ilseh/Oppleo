import logging

from nl.oppleo.utils.ModulePresence import modulePresence
from nl.oppleo.services.LedPinDefinition import LedPinDefinition
from nl.oppleo.services.LedLightProdHardware import LedLightProdHardware

# Interval in ms to update led light
FREQ_MS_TO_UPDATE_LED = 10

class LedLightProd(object):
    __logger = None
    __pinDefinition:LedPinDefinition = None
    __hardware:LedLightProdHardware = None
    __pwm = None
    __intensity = 0

    def __init__(self, pinDefinition:LedPinDefinition, intensity:int=0, pwm=None):
        self.__logger = logging.getLogger('nl.oppleo.services.LedLightProd')
        self.__pinDefinition = pinDefinition
        self.__hardware = LedLightProdHardware(pinDefinition=pinDefinition)
        self.__pwm = pwm
        self.__intensity = intensity

    def on(self):
        self.__logger.debug('LedLightProd.on() - Starting led light {} (intensity {})'.format(self.__pinDefinition.color, self.__intensity))
        self.__pwm = self.__hardware.init_gpio_pwm()
        if self.__pwm is None:
            self.__logger.debug('LedLightProd.on() - Led light{} not started (intensity {})'.format(self.__pinDefinition.color, self.__intensity))
            return
        try:
            self.__pwm.start(0)
            self.__logger.debug('LedLightProd.on() - Started led light {} (intensity {})'.format(self.__pinDefinition.color, self.__intensity))
            self.__pwm.ChangeDutyCycle(self.__intensity)
        except Exception as e:
            self.__logger.error('LedLightProd.on() - Exception lighting led {}'.format(str(e)))

    def off(self):
        self.__logger.debug('LedLightProd.off() - Stopping led light {} (intensity {})'.format(self.__pinDefinition.color, self.__intensity))
        if self.__pwm is None:
            self.__logger.debug('LedLightProd.off() - Led light {} not stopped (intensity {})'.format(self.__pinDefinition.color, self.__intensity))
            return
        try:
            self.__pwm.stop()
        except Exception as e:
            self.__logger.debug('LedLightProd.off() - Could not stop pwm {} assume not running {})'.format(self.__pinDefinition.color, str(e)))


    def cleanup(self):
        self.__hardware.cleanup()