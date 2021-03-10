import logging

"""
    Dummy GPIO object 
"""

class DummyGPIOPWM(object):
    __logger = None

    def __init__(self):
        self.__logger = logging.getLogger('nl.oppleo.utils.DummyGPIOPWM')
        self.__logger.debug("DummyGPIOPWM.init()")

    def ChangeDutyCycle(self, *param):
        self.__logger.debug("DummyGPIOPWM.ChangeDutyCycle({})".format(','.join(str(param))))

    def start(self, *param):
        self.__logger.debug("DummyGPIOPWM.start({})".format(','.join(str(param))))

    def stop(self, *param):
        self.__logger.debug("DummyGPIOPWM.stop({})".format(','.join(str(param))))



class DummyGPIO(object):
    __logger = None
    BOARD = 0
    BCM = 1
    OUT = 3
    IN = 4
    HIGH = 5
    LOW = 6
    
    def __init__(self):
        self.__logger = logging.getLogger('nl.oppleo.utils.DummyGPIO')
        self.__logger.debug("DummyGPIO.init()")

    def setmode(self, *param):
        self.__logger.debug("DummyGPIO.setmode({})".format(','.join(str(param))))

    def setwarnings(self, *param):
        self.__logger.debug("DummyGPIO.setwarnings({})".format(','.join(str(param))))

    def setup(self, *param, initial:int=-1):
        self.__logger.debug("DummyGPIO.setup({}{})".format(','.join(str(param)), '' if initial == -1 else ',initial={}'.format(str(initial))))
    
    def PWM(self, *param):
        self.__logger.debug("DummyGPIO.PWM({})".format(','.join(str(param))))
        return DummyGPIOPWM()

    def output(self, *param):
        self.__logger.debug("DummyGPIO.output({})".format(','.join(str(param))))

    def input(self, *param):
        import random
        random_boolean = bool(random.getrandbits(1))
        self.__logger.debug("DummyGPIO.input({}) - will return {}".format(','.join(str(param)), 
                                ("True" if random_boolean == True else "False")
                            ))
        return random_boolean

    def cleanup(self, *param):
        self.__logger.debug("DummyGPIO.cleanup({})".format(','.join(str(param))))
