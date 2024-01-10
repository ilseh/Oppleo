import logging

from nl.oppleo.config.OppleoSystemConfig import OppleoSystemConfig

oppleoSystemConfig = OppleoSystemConfig()
"""
    Stub GPIO object 
"""

class GPIOPWM_stub(object):
    __logger = None

    def __init__(self):
        self.__logger = logging.getLogger(__name__)
        self.__logger.setLevel(level=oppleoSystemConfig.getLogLevelForModule(__name__))   
        self.__logger.debug("GPIOPWM_stub.init()")

    def __format(self, params):
        s = None
        for param in params:
            s = str(param) if s is None else s + ',' + str(param)
        return s

    def ChangeDutyCycle(self, *param):
        self.__logger.debug("GPIOPWM_stub.ChangeDutyCycle({})".format(self.__format(param)))

    def start(self, *param):
        self.__logger.debug("GPIOPWM_stub.start({})".format(self.__format(param)))

    def stop(self, *param):
        self.__logger.debug("GPIOPWM_stub.stop({})".format(self.__format(param)))



class GPIO_stub(object):
    __logger = None
    BOARD = 10
    BCM = 11

    IN = 1
    OUT = 0

    HIGH = 1
    LOW = 0

    SERIAL = 40
    SPI = 41
    I2C = 42
    HARD_PWM = 43
    UNKNOWN = -1

    PUD_DOWN = 21
    PUD_UP = 22
   
    RISING = 31
    FALLING = 32
    BOTH = 33

    # GPIO.RPI_INFO: {'P1_REVISION': 3, 'REVISION': 'b03111', 'TYPE': 'Pi 4 Model B', 'MANUFACTURER': 'Sony', 'PROCESSOR': 'BCM2711', 'RAM': '2G'}
    RPI_INFO = { 'P1_REVISION': 'stub', 'RAM': '0M', 'REVISION': 'stub', 'TYPE': 'stub', 'PROCESSOR': 'stub', 'MANUFACTURER': 'stub'}
    # GPIO.RPI_REVISION: 3
    RPI_REVISION = 0
    # GPIO.VERSION: 0.7.0
    VERSION = '0.0.0'

    def __init__(self):
        self.__logger = logging.getLogger(__name__)
        self.__logger.setLevel(level=oppleoSystemConfig.getLogLevelForModule(__name__))   
        self.__logger.debug("GPIO_stub.init()")

    def __format(self, params=None):
        if params is None:
            return ''
        s = None
        for param in params:
            s = str(param) if s is None else s + ',' + str(param)
        return s

    def setmode(self, *param):
        self.__logger.debug("GPIO_stub.setmode({})".format(self.__format(param)))

    def setwarnings(self, *param):
        self.__logger.debug("GPIO_stub.setwarnings({})".format(self.__format(param)))

    def setup(self, *param, initial:int=-1, pull_up_down:int=-1):
        self.__logger.debug("GPIO_stub.setup({}{}{})".format(self.__format(param), 
                                                             '' if initial == -1 else ',initial={}'.format(str(initial)),
                                                             '' if pull_up_down == -1 else ',pull_up_down={}'.format(str(pull_up_down))
                                                            )
                            )
    
    def PWM(self, *param):
        self.__logger.debug("GPIO_stub.PWM({})".format(self.__format(param)))
        return GPIOPWM_stub()

    def output(self, *param):
        self.__logger.debug("GPIO_stub.output({})".format(self.__format(param)))

    def input(self, *param):
        import random
        random_boolean = bool(random.getrandbits(1))
        self.__logger.debug("GPIO_stub.input({}) - will return {}".format(self.__format(param), 
                                ("True" if random_boolean == True else "False")
                            ))
        return random_boolean

    def gpio_function(self, *param):
        self.__logger.debug("GPIO_stub.gpio_function({})".format(self.__format(param)))
        return self.OUT

    def wait_for_edge(self, *param):
        self.__logger.debug("GPIO_stub.wait_for_edge({})".format(self.__format(param)))

    def wait_foevent_detectedr_edge(self, *param):
        self.__logger.debug("GPIO_stub.event_detected({})".format(self.__format(param)))

    def add_event_detect(self, *param):
        self.__logger.debug("GPIO_stub.add_event_detect({})".format(self.__format(param)))

    def cleanup(self, *param):
        self.__logger.debug("GPIO_stub.cleanup({})".format(self.__format(param)))
