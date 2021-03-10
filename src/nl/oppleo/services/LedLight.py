# https://raspberrytips.nl/kaarslicht-pwm-raspberry-pi/

import logging

from nl.oppleo.services.LedLightDev import LedLightDev

from nl.oppleo.config.OppleoSystemConfig import OppleoSystemConfig
from nl.oppleo.utils.ModulePresence import modulePresence
from nl.oppleo.services.LedLightPulseProd import LedLightPulseProd
from nl.oppleo.services.LedLightProd import LedLightProd

oppleoSystemConfig = OppleoSystemConfig()


class LedLight(object):
    __logger = None
    __services = None
    __combinedColorName = "Unknown"

    def __init__(self, *pinDefinitions, combinedColorName, intensity, pulse=False, services=[]):
        self.__logger = logging.getLogger('nl.oppleo.services.LedLight')
        self.__services = services
        self.__combinedColorName = combinedColorName

        for pinDefinition in pinDefinitions:
            if oppleoSystemConfig.oppleoLedEnabled:
                self.__services.append(
                    LedLightPulseProd(pinDefinition=pinDefinition, intensity=intensity) if pulse else 
                        LedLightProd(pinDefinition=pinDefinition, intensity=intensity)
                    )
            else:
                self.__services.append(LedLightDev(pinDefinition, intensity=intensity))

        self.__logger.debug('LedLight.init() - Initialize with %d ledlights %s' % (len(self.__services), "to pulse" if pulse else "no pulse"))

    def on(self):
        self.__logger.debug("LedLight.on() {}".format(self.__combinedColorName))
        for service in self.__services:
            service.on()

    def off(self):
        self.__logger.debug("LedLight.off() {}".format(self.__combinedColorName))
        for service in self.__services:
            service.off()

    def cleanup(self):
        self.__logger.debug("LedLight.cleanup() {}".format(self.__combinedColorName))
        for service in self.__services:
            service.cleanup()
