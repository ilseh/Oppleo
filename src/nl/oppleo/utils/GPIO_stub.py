import logging

"""
    Stub GPIO object 
"""

class GPIOPWM_stub(object):
    __logger = None

    def __init__(self):
        self.__logger = logging.getLogger('nl.oppleo.utils.GPIOPWM_stub')
        self.__logger.debug("GPIOPWM_stub.init()")

    def ChangeDutyCycle(self, *param):
        self.__logger.debug("GPIOPWM_stub.ChangeDutyCycle({})".format(','.join(str(param))))

    def start(self, *param):
        self.__logger.debug("GPIOPWM_stub.start({})".format(','.join(str(param))))

    def stop(self, *param):
        self.__logger.debug("GPIOPWM_stub.stop({})".format(','.join(str(param))))



class GPIO_stub(object):
    __logger = None
    BOARD = 0
    BCM = 1
    OUT = 3
    IN = 4
    HIGH = 5
    LOW = 6
    
    def __init__(self):
        self.__logger = logging.getLogger('nl.oppleo.utils.GPIO_stub')
        self.__logger.debug("GPIO_stub.init()")

    def setmode(self, *param):
        self.__logger.debug("GPIO_stub.setmode({})".format(','.join(str(param))))

    def setwarnings(self, *param):
        self.__logger.debug("GPIO_stub.setwarnings({})".format(','.join(str(param))))

    def setup(self, *param, initial:int=-1):
        self.__logger.debug("GPIO_stub.setup({}{})".format(','.join(str(param)), '' if initial == -1 else ',initial={}'.format(str(initial))))
    
    def PWM(self, *param):
        self.__logger.debug("GPIO_stub.PWM({})".format(','.join(str(param))))
        return GPIOPWM_stub()

    def output(self, *param):
        self.__logger.debug("GPIO_stub.output({})".format(','.join(str(param))))

    def input(self, *param):
        import random
        random_boolean = bool(random.getrandbits(1))
        self.__logger.debug("GPIO_stub.input({}) - will return {}".format(','.join(str(param)), 
                                ("True" if random_boolean == True else "False")
                            ))
        return random_boolean

    def cleanup(self, *param):
        self.__logger.debug("GPIO_stub.cleanup({})".format(','.join(str(param))))
