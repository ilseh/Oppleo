
import logging
import time
from nl.carcharging.config.WebAppConfig import WebAppConfig
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
        global WebAppConfig
        # SimpleMFRC522() read() blocks other threads, call no block instead to allow other threads to run
        #   return self.reader.read()
        id = None
        text = None
        lastRun = 0
        while id is None:
            # This call returns every time, with id is None when no rfid tag was detected
            id, text = self.reader.read_no_block()
            """
            TODO Off peak hours
            if check for offpeak
                if off peak and reader is enabled but evse is not, go ahead and open evse 
                    (and possibly wake car for charging)
                    oh, and reset any 'over-ride off peak for once' authorizations
                if not off peak and reader is enabled, go ahead and close evse
                    maybe warn through prowl?
            Check only once per 1 or 5 minutes, to prevent database overload and bad rfid response 
            """
            # Sleep is interruptable by other threads, but sleeing 7 seconds before checking if 
            # stop is requested is a bit long, so sleep for 0.1 seconds, then check passed time
            if (time.time() *1000.0) > (lastRun + (WebAppConfig.off_peak_check_interval *1000.0)):
                # time to run again

                """
                from nl.carcharging.models.OffPeakHoursModel import OffPeakHoursModel
                ohm = OffPeakHoursModel()
                is_op = ohm.is_off_peak_now()
                if is_op and 
                """

                lastRun = time.time() *1000.0
            # Sleep for just a little to yield for other threads
            WebAppConfig.appSocketIO.sleep(0.05)

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

