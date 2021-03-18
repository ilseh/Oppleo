# https://raspberrytips.nl/kaarslicht-pwm-raspberry-pi/

from typing import Optional
import logging

from nl.oppleo.config.OppleoSystemConfig import OppleoSystemConfig

from nl.oppleo.utils.ModulePresence import modulePresence
from nl.oppleo.services.led.LedPinBehaviour import LedPinBehaviour



oppleoSystemConfig = OppleoSystemConfig()

"""
    frequency is the number of pulses in 1 second for switching or pulsing from low to high and vice versa.
    the frequency of the dutycycle is set to 100Hz (invisible blinking speed).
"""

class RGBLedEffect(object):
    EFFECT_STATIC = 1
    EFFECT_PULSING = 2
    EFFECT_SWITCHING = 3
    VALID_EFFECTS = [ EFFECT_STATIC, EFFECT_PULSING, EFFECT_SWITCHING ]
    
    __logger = None
    __red:Optional[LedPinBehaviour] = None
    __green:Optional[LedPinBehaviour] = None
    __blue:Optional[LedPinBehaviour] = None
    __frequency:int = 0
    __effect:int = EFFECT_STATIC
    __combinedColorName:str = "Unknown"

    def __init__(self, 
                 red:LedPinBehaviour=None, 
                 green:LedPinBehaviour=None, 
                 blue:LedPinBehaviour=None, 
                 effect:int=0, 
                 frequency:int=0, 
                 combinedColorName:str="Unknown"):
        self.__logger = logging.getLogger('nl.oppleo.services.RGBLedEffect')
        self.__red = red
        self.__green = green
        self.__blue = blue
        self.__effect = effect if effect in self.VALID_EFFECTS else self.EFFECT_STATIC
        self.__frequency = frequency
        self.__combinedColorName = combinedColorName

    @property
    def red(self):
        return self.__red
            
    @red.setter
    def red(self, value:LedPinBehaviour=None):
        self.__red = value

    @property
    def green(self):
        return self.__green
            
    @green.setter
    def green(self, value:LedPinBehaviour=None):
        self.__green = value

    @property
    def blue(self):
        return self.__blue
            
    @blue.setter
    def blue(self, value:LedPinBehaviour=None):
        self.__blue = value

    @property
    def frequency(self):
        return self.__frequency
            
    @frequency.setter
    def frequency(self, value:int=0):
        self.__frequency = value

    @property
    def effect(self):
        return self.__effect
            
    @effect.setter
    def effect(self, value:int=0):
        self.__effect = value


    @property
    def combinedColorName(self):
        return self.__combinedColorName
            
    @combinedColorName.setter
    def combinedColorName(self, value:str="Unknown"):
        self.__combinedColorName = value


    """
        Calculated value
    """
    @property
    def static(self):
        return (self.__effect != self.EFFECT_SWITCHING and
                self.__effect != self.EFFECT_PULSING)

    """
        Calculated value
    """
    @property
    def switching(self):
        return self.__effect == self.EFFECT_SWITCHING

    """
        Calculated value
    """
    @property
    def pulsing(self):
        return self.__effect == self.EFFECT_PULSING

