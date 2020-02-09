
import logging
from nl.carcharging.utils.GenericUtil import GenericUtil
try:
    from mfrc522 import SimpleMFRC522
except RuntimeError:
    logging.debug('Assuming dev env')
except ModuleNotFoundError:
    logging.debug('Assuming dev env')

LOGGER_PATH = "nl.carcharging.service.RfidReader"

class RfidReaderDev(object):

    def read(self):
        return 333, "Rfid 333"




class RfidReaderProd(object):

    def __init__(self):
        self.reader = SimpleMFRC522()

    def read(self):
        return self.reader.read()




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

