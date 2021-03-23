import logging

"""
    Stub pigpio object 
"""

class pi_stub(object):
    __logger = None

    def __init__(self):
        self.__logger = logging.getLogger('nl.oppleo.utils.stubs.pi_stub')
        self.__logger.debug("pi_stub.init()")

    def __format(self, params=None):
        if params is None:
            return ''
        s = None
        for param in params:
            s = str(param) if s is None else s + ',' + str(param)
        return s

    def callback(self, *param):
        self.__logger.debug("pigpio_stub.callback({})".format(self.__format(param)))

    def stop(self, *param):
        self.__logger.debug("pigpio_stub.stop({})".format(self.__format(param)))


class pigpio_stub(object):
    __logger = None

    EITHER_EDGE = 1

    def __init__(self):
        self.__logger = logging.getLogger('nl.oppleo.utils.pigpio_stub')
        self.__logger.debug("pigpio_stub.init()")

    def __format(self, params):
        s = None
        for param in params:
            s = str(param) if s is None else s + ',' + str(param)
        return s

    def pi(self, *param):
        self.__logger.debug("pigpio_stub.pi({})".format(self.__format(param)))
        return pi_stub()

    def tickDiff(self, *param):
        self.__logger.debug("pigpio_stub.tickDiff({})".format(self.__format(param)))
