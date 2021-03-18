import logging

"""
    high/low intensity is the percentage (0-100) of brightness, using the dutycycle of pwm.
"""

class LedPinBehaviour(object):
    __logger = None
    __pin = 0
    __low_intensity = 0
    __high_intensity = 0

    def __init__(self, 
                 pin:int=0, 
                 low_intensity:int=0, 
                 high_intensity:int=0):
        self.__logger = logging.getLogger('nl.oppleo.services.LedPinBehaviour')

        self.__pin = pin
        if low_intensity < 0:
            self.__low_intensity = 0
        elif low_intensity > 100:
            self.__low_intensity = 100
        else:
            self.__low_intensity = low_intensity
        if high_intensity < 0:
            self.__high_intensity = 0
        elif high_intensity > 100:
            self.__high_intensity = 100
        else:
            self.__high_intensity = high_intensity

        self.__logger.debug("LedPinBehaviour.init() pin:{}, low_intensity:{}, high_intensity:{}".format(
                                pin, low_intensity, high_intensity))

    @property
    def pin(self):
        return self.__pin

    @pin.setter
    def pin(self, value:int=0):
        self.__pin = value


    @property
    def low_intensity(self):
        return self.__low_intensity

    @low_intensity.setter
    def low_intensity(self, value:int=0):
        if value < 0:
            self.__low_intensity = 0
        if value > 100:
            self.__low_intensity = 100
        self.__low_intensity = value


    @property
    def high_intensity(self):
        return self.__high_intensity

    @high_intensity.setter
    def high_intensity(self, value:int=0):
        if value < 0:
            self.__high_intensity = 0
        if value > 100:
            self.__high_intensity = 100
        self.__high_intensity = value


    """
        Calculated value
    """
    @property
    def staticEffect(self):
        return self.__high_intensity == self.__low_intensity

    """
        Calculated value
    """
    @property
    def dynamicEffect(self):
        return self.__high_intensity != self.__low_intensity

    """
        Calculated value
    """
    @property
    def dimmed(self):
        return ((self.__high_intensity != 0 or self.__high_intensity != 100) and
                (self.__low_intensity != 0 or self.__low_intensity != 100))
