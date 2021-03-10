import logging

class LedPinDefinition(object):
    __logger = None
    __pin = 0
    __color = "Unknown"

    def __init__(self, pin:int=0, color:str="Unknown"):
        self.__logger = logging.getLogger('nl.oppleo.services.LedPinDefinition')

        self.__pin = pin
        self.__color = color

        self.__logger.debug("LedPinDefinition.init() pin:{} color:{}".format(pin, color))

    @property
    def pin(self):
        return self.__pin

    @pin.setter
    def pin(self, value:int=0):
        self.__pin = value

    @property
    def color(self):
        return self.__color

    @color.setter
    def color(self, value:str="Unknown"):
        self.__color = value
