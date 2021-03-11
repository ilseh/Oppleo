import logging
from nl.oppleo.utils.GPIO_stub import GPIO_stub

"""
"""

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class ModulePresence(object, metaclass=Singleton):
    """
        Private variables
    """
    __logger = None

    __enable_GPIO_stub = True


    """ Libraries installed """
    __mfrc522 = False
    __rpigpio = False
    __GPIO = None


    def __init__(self):
        self.logger = logging.getLogger('nl.oppleo.utils.ModulePresence')

        try:
            from mfrc522 import SimpleMFRC522
            __mfrc522 = True
        except RuntimeError as re:
            self.logger.warning('SimpleMFRC522 (mfrc522) RuntimeError - possible privilege issue.')
        except ModuleNotFoundError as mnfe:
            self.logger.warning('SimpleMFRC522 (mfrc522) not installed.')

        try:
            import RPi.GPIO as GPIO
            self.__rpigpio = True
            self.__GPIO = GPIO
        except RuntimeError:
            self.logger.debug('GPIO (RPi) RuntimeError - possible privilege issue.')
        except ModuleNotFoundError:
            self.logger.debug('GPIO (RPi) not installed.')

        if self.__enable_GPIO_stub and not self.__rpigpio:
            self.logger.debug('GPIO_stub enabled (GPIO not installed)')
            self.__rpigpio = True
            self.__GPIO = GPIO_stub()


    """
        mfrc522
    """
    def simpleMFRC522Available(self):
        return self.__mfrc522

    """
        rpigpio
    """
    def gpioAvailable(self):
        return self.__rpigpio and self.__GPIO is not None

    """
        GPIO
    """
    @property
    def GPIO(self):
        return self.__GPIO



"""
    Initialize the singleton
"""
modulePresence = ModulePresence()


