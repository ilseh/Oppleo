
import logging
import time
import json

from nl.oppleo.utils.ModulePresence import modulePresence
from nl.oppleo.config.OppleoSystemConfig import OppleoSystemConfig
from nl.oppleo.config.OppleoConfig import OppleoConfig

oppleoSystemConfig = OppleoSystemConfig()
oppleoConfig = OppleoConfig()


class RfidReader(object):
    __logger = None

    def __init__(self):
        self.__logger = logging.getLogger(__name__)
        self.__logger.setLevel(level=oppleoSystemConfig.getLogLevelForModule(__name__))       
        # TODO: get from modulePresence

        if modulePresence.OppleoMFRC522Available:
            modulePresence.OppleoMFRC522.setup(bus=-1, 
                                               device=-1,
                                               speed=-1,
                                               GPIO=modulePresence.GPIO,
                                               pin_rst=-1,
                                               antennaBoost=False
                                               )

    """
        Read function using the pimylifeup SimpleMFRC522 class to access MFRC522 class.
        Note that the read() call on the SimpleMFRC522 basically implements this function without yield (sleep).
        This function as the issue of loosing connection after a while resulting in no longer reading the RFID tags.
    """
    def read(self):
        global modulePresence
        
        if modulePresence.OppleoMFRC522_IsStub:
            self.__logger.warn("Reading from stub (don't expect reading any values)")

        # OppleoMFRC522() read() does not lock other threads, no need to call read_no_block() instead to yield
        # This call returns with id when an rfid tag was detected
        return modulePresence.OppleoMFRC522.read(select=False, auth=False) # return id, text
      
    """
        Read function using the pimylifeup SimpleMFRC522 class to access MFRC522 class.
        Note that the read() call on the SimpleMFRC522 basically implements this function without yield (sleep).
        This function as the issue of loosing connection after a while resulting in no longer reading the RFID tags.
    """
    def read_SimpleMFRC522(self):
        global oppleoConfig, modulePresence
        
        if modulePresence.SimpleMFRC522_IsStub:
            self.__logger.warn("Reading from stub (don't expect reading any values)")

        # SimpleMFRC522() read() blocks other threads, call read_no_block() instead to yield to other threads.
        while True:
            if oppleoSystemConfig.rfidEnabled:
                # This call returns every time, with id is None when no rfid tag was detected
                id, text = modulePresence.SimpleMFRC522.read_no_block()
                if id is not None:
                    return id, text
            # else:
                # RFID SPI Not enabled.
                # pass
            # Sleep for just a little to yield for other threads
            if oppleoConfig.appSocketIO is not None:
                oppleoConfig.appSocketIO.sleep(0.05)
            else:
                time.sleep(0.05)


    """ Function to read the MFRC522 log """
    def read_log(self):
        global modulePresence

        if modulePresence.OppleoMFRC522_IsStub:
            self.__logger.warn("Reading from stub (don't expect reading any values)")
            return {}

        return modulePresence.OppleoMFRC522.oLog.to_str()

    def diag(self):
        return json.dumps({
            "OppleoMFRC522_IsStub": modulePresence.OppleoMFRC522_IsStub,
            "OppleoMFRC522Available": modulePresence.OppleoMFRC522Available,
            "log": self.read_log()
            }, 
            default=str     # Overcome "TypeError: Object of type datetime is not JSON serializable"
        )
