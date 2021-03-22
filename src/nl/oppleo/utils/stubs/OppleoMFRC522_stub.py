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

    def setup(self, *param):
        self.__logger.debug("OppleoMFRC522_stub.setup({})".format(self.__format(param)))


    def read(self, *param):
        self.__logger.debug("OppleoMFRC522_stub.read({})".format(self.__format(param)))
        # For now, never return from this read action
        while True:
            time.sleep(.5)

    def read_no_block(self, *param):
        self.__logger.debug("OppleoMFRC522_stub.read_no_block({})".format(self.__format(param)))
        # Return empty values from this read action

        return None, ''

