
import logging
import time
from nl.oppleo.config.OppleoConfig import OppleoConfig
from nl.oppleo.utils.GenericUtil import GenericUtil
try:
    from mfrc522 import SimpleMFRC522
except RuntimeError:
    logging.debug('Assuming dev env')
except ModuleNotFoundError:
    logging.debug('Assuming dev env')

LOGGER_PATH = "nl.oppleo.service.RfidReader"

class RfidReaderDev(object):

    def read(self):
        return 333, "Rfid 333"



class RfidReaderProd(object):

    def __init__(self):
        self.reader = SimpleMFRC522()


    def read(self):
        global OppleoConfig
        # SimpleMFRC522() read() blocks other threads, call no block instead to allow other threads to run
        #   return self.reader.read()
        id = None
        text = None
        while id is None:
            # This call returns every time, with id is None when no rfid tag was detected
            id, text = self.reader.read_no_block()
            # Sleep for just a little to yield for other threads
            OppleoConfig.appSocketIO.sleep(0.05)

        return id, text








class RfidReader(object):

    def __init__(self):
        self.logger = logging.getLogger(LOGGER_PATH)
        if GenericUtil.isProd():
            self.logger.debug("Using production rfid reader")
            self.reader = RfidReaderProd()
        else:
            self.logger.debug("Using fake rfid reader")
            self.reader = RfidReaderDev()


    def read(self):
        return self.reader.read()

