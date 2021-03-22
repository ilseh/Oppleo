import logging
import time

"""
    Stub OppleoMFRC522 object 
"""


class OppleoMFRC522_stub(object):
    __logger = None

    def __init__(self):
        self.__logger = logging.getLogger('nl.oppleo.utils.stubs.OppleoMFRC522_stub')
        self.__logger.debug("OppleoMFRC522_stub.init()")

    def __format(self, params=None):
        if params is None:
            return ''
        s = None
        for param in params:
            s = str(param) if s is None else s + ',' + str(param)
        return s

    def setup(self, *param, bus=-1, device=-1, speed=-1, GPIO=None, pin_rst=-1, antennaBoost=False):
        self.__logger.debug("OppleoMFRC522_stub.setup({}, bus={}, device={}, speed={}, GPIO={}, pin_rst={}, antennaBoost={})".format(
            self.__format(param), bus, device, speed, GPIO, pin_rst, antennaBoost))

    def read(self, *param, select=False, auth=False):
        self.__logger.debug("OppleoMFRC522_stub.read({}, select={}, auth={})".format(self.__format(param), select, auth))
        # For now, never return from this read action
        while True:
            time.sleep(5)
            return '584190412223', ''
#            time.sleep(.5)

    def read_no_block(self, *param, select=False, auth=False):
        self.__logger.debug("OppleoMFRC522_stub.read_no_block({}, select={}, auth={})".format(self.__format(param), select, auth))
        # Return empty values from this read action

        return None, ''

