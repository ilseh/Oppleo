import logging
from nl.oppleo.utils.GPIO_stub import GPIO_stub
from nl.oppleo.utils.pigpio_stub import pigpio_stub

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
    __enable_pigpio_stub = True


    """ Libraries installed """
    __mfrc522_installed = False
    __pigpio_installed  = False
    __rgpio_installed   = False
    """ Modules or stubs """
    __GPIO              = None
    __pigpio            = None


    def __init__(self):
        self.logger = logging.getLogger('nl.oppleo.utils.ModulePresence')

        try:
            from mfrc522 import SimpleMFRC522
            self.__mfrc522_installed = True
        except RuntimeError as re:
            self.logger.warning('SimpleMFRC522 (mfrc522) RuntimeError - possible privilege issue.')
        except ModuleNotFoundError as mnfe:
            self.logger.warning('SimpleMFRC522 (mfrc522) not installed.')


        try:
            import pigpio
            self.__pigpio_installed = True
        except ModuleNotFoundError:
            self.logger.debug('PiGPIO not installed.')

        if self.__enable_pigpio_stub and not self.__pigpio_installed:
            self.logger.warning('pigpio_stub enabled (pigpio not installed)')
            self.__pigpio_installed = True
            self.__pigpio = pigpio_stub()


        try:
            import RPi.GPIO as GPIO
            self.__rgpio_installed = True
            self.__GPIO = GPIO
        except RuntimeError:
            self.logger.debug('GPIO (RPi) RuntimeError - possible privilege issue.')
        except ModuleNotFoundError:
            self.logger.debug('GPIO (RPi) not installed.')

        if self.__enable_GPIO_stub and not self.__rgpio_installed:
            self.logger.warning('GPIO_stub enabled (GPIO not installed)')
            self.__rgpio_installed = True
            self.__GPIO = GPIO_stub()




    """
        mfrc522
    """
    def simpleMFRC522Available(self):
        return self.__mfrc522_installed


    """
        rpigpio
    """
    def gpioAvailable(self):
        return self.__rgpio_installed and self.__GPIO is not None

    """
        GPIO
    """
    @property
    def GPIO(self):
        return self.__GPIO


    """
        GPIO
    """
    @property
    def GPIO_IsStub(self) -> bool:
        return isinstance(self.__GPIO, GPIO_stub)


    """
        pigpio
    """
    def pigpioAvailable(self):
        return self.__pigpio_installed and self.__pigpio is not None


    """
        pigpio
    """
    @property
    def pigpio(self):
        return self.__pigpio


    """
        pigpio
    """
    @property
    def pigpio_IsStub(self) -> bool:
        return isinstance(self.__GPIO, pigpio_stub)


"""
    Initialize the singleton
"""
modulePresence = ModulePresence()


