import logging
import time

"""
    Stub SimpleMFRC522 object 
"""


class SimpleMFRC522_stub(object):
    __logger = None

    def __init__(self):
        self.__logger = logging.getLogger('nl.oppleo.utils.stubs.SimpleMFRC522_stub')
        self.__logger.debug("SimpleMFRC522_stub.init()")

    def __format(self, params=None):
        if params is None:
            return ''
        s = None
        for param in params:
            s = str(param) if s is None else s + ',' + str(param)
        return s

    def read(self, *param):
        self.__logger.debug("SimpleMFRC522_stub.read({})".format(self.__format(param)))
        # For now, never return from this read action
        while True:
            time.sleep(.5)

    def read_no_block(self, *param):
        self.__logger.debug("SimpleMFRC522_stub.read_no_block({})".format(self.__format(param)))
        # Return empty values from this read action

        return None, ''

