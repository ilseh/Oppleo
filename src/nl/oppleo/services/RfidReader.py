
import logging
import time
from nl.oppleo.config.OppleoSystemConfig import OppleoSystemConfig
from nl.oppleo.config.OppleoConfig import OppleoConfig
from nl.oppleo.utils.GenericUtil import GenericUtil

oppleoSystemConfig = OppleoSystemConfig()
oppleoConfig = OppleoConfig()

LOGGER_PATH = "nl.oppleo.service.RfidReader"
logger = logging.getLogger(LOGGER_PATH)

try:
    from mfrc522 import SimpleMFRC522
except RuntimeError as re:
    logger.debug('RuntimeError {} importing SimpleMFRC522. Probably not installed.'.format(str(re)))
except ModuleNotFoundError as mnfe:
    logger.debug('ModuleNotFoundError {} importing SimpleMFRC522. Probably not installed.'.format(str(mnfe)))


class RfidReaderDev(object):

    def read(self):
        return 333, "Rfid 333"



class SimpleMFRC522RfidReader(object):

    def __init__(self):
        self.logger = logging.getLogger('nl.oppleo.services.SimpleMFRC522RfidReader')
        # Raises NameError if package is not installed
        self.reader = SimpleMFRC522()


    def read(self):
        global oppleoConfig
        # SimpleMFRC522() read() blocks other threads, call no block instead to allow other threads to run
        #   return self.reader.read()
        id = None
        text = None
        while id is None:
            # This call returns every time, with id is None when no rfid tag was detected
            id, text = self.reader.read_no_block()
            # Sleep for just a little to yield for other threads
            oppleoConfig.appSocketIO.sleep(0.05)

        return id, text


class RfidReader(object):
    simpleMFRC522RfidReader = None

    def __init__(self):
        self.logger = logging.getLogger("nl.oppleo.service.RfidReader")
        if oppleoSystemConfig.rfidEnabled:
            self.logger.debug("Enabling MFRC522 RFID reader")
            try:
                self.simpleMFRC522RfidReader = SimpleMFRC522RfidReader()
            except NameError as ne:
                self.logger.warn("NameError {} - Enabling MFRC522 RFID reader failed (not installed). Most likely a configuration error.".format(str(ne)))
        else:
            self.logger.debug("Not enabling rfid reader")
            self.simpleMFRC522RfidReader = None

    def read(self):
        if self.simpleMFRC522RfidReader is None:
            # block the read, do not return
            while True:
                # Sleep for just a little to yield for other threads
                oppleoConfig.appSocketIO.sleep(0.7)
        # if there is a reader, use it
        return self.simpleMFRC522RfidReader.read()
