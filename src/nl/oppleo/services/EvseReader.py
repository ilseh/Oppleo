
import logging
import os
import sys
import traceback

from nl.oppleo.config.OppleoSystemConfig import OppleoSystemConfig
from nl.oppleo.config.OppleoConfig import OppleoConfig
from nl.oppleo.services.EvseReaderProd import EvseReaderProd, EvseState
from nl.oppleo.utils.ModulePresence import modulePresence

LOGGER_PATH = "nl.oppleo.service.EvseReader"
oppleoSystemConfig = OppleoSystemConfig()
oppleoConfig = OppleoConfig()
logger = logging.getLogger(LOGGER_PATH)



class EvseReaderDev(object):
    def __init__(self):
        self.logger = logging.getLogger(LOGGER_PATH + 'Dev')

    def loop(self, cb_until, cb_result):
        global oppleoConfig

        cb_result(EvseState.EVSE_STATE_UNKNOWN)
        self.logger.debug('Fake run Evse Read loop')
        while not cb_until():
            oppleoConfig.appSocketIO.sleep(0.8)


class EvseReader(object):

    def __init__(self):
        self.logger = logging.getLogger(LOGGER_PATH)
        if oppleoSystemConfig.evseLedReaderEnabled:
            self.logger.debug("Using production Evse reader")
            self.reader = EvseReaderProd()
        else:
            self.logger.debug("Using fake Evse reader")
            self.reader = EvseReaderDev()

    def loop(self, cb_until, cb_result):
        try:
            self.reader.loop(cb_until, cb_result)
        except Exception as e:
            self.logger.error('Could not start EvseReader loop ({})'.format(str(e)))
