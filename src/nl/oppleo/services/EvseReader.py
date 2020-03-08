
import logging
import os
import sys
import traceback

from nl.oppleo.config.OppleoConfig import OppleoConfig
from nl.oppleo.services.EvseReaderProd import EvseReaderProd, EvseState
from nl.oppleo.utils.GenericUtil import GenericUtil

LOGGER_PATH = "nl.oppleo.service.EvseReader"
oppleoConfig = OppleoConfig()
logger = logging.getLogger(LOGGER_PATH)

try:
    from mfrc522 import SimpleMFRC522
except RuntimeError:
    logger.debug('Assuming dev env')
except ModuleNotFoundError:
    logger.debug('Assuming dev env')



class EvseReaderDev(object):
    def __init__(self):
        self.logger = logging.getLogger(LOGGER_PATH + 'Dev')

    def loop(self, cb_until, cb_result):
        global oppleoConfig
        while not cb_until():
            self.logger.debug('Fake run Evse Read loop')
            oppleoConfig.appSocketIO.sleep(0.5)
            cb_result(EvseState.EVSE_STATE_UNKNOWN)


class EvseReader(object):

    def __init__(self):
        self.logger = logging.getLogger(LOGGER_PATH)
        if GenericUtil.isProd():
            self.logger.debug("Using production Evse reader")
            self.reader = EvseReaderProd()
        else:
            self.logger.debug("Using fake Evse reader")
            self.reader = EvseReaderDev()

    def loop(self, cb_until, cb_result):
        try:
            self.reader.loop(cb_until, cb_result)
        except Exception as ex:
            self.logger.exception('Could not start EvseReader loop')
