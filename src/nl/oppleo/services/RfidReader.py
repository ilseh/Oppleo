
import logging
import time
from nl.oppleo.utils.ModulePresence import modulePresence
from nl.oppleo.config.OppleoSystemConfig import OppleoSystemConfig
from nl.oppleo.config.OppleoConfig import OppleoConfig

oppleoSystemConfig = OppleoSystemConfig()
oppleoConfig = OppleoConfig()


class RfidReader(object):

    def __init__(self):
        self.logger = logging.getLogger("nl.oppleo.service.RfidReader")

    def read(self):
        global oppleoConfig, modulePresence
        
        if modulePresence.SimpleMFRC522_IsStub:
            self.logger.warn("read() - Reading from stub (don't expect reading any values)")

        # SimpleMFRC522() read() blocks other threads, call read_no_block() instead to yield to other threads.
        while True:
            # This call returns every time, with id is None when no rfid tag was detected
            id, text = modulePresence.SimpleMFRC522.read_no_block()
            if id is not None:
                return id, text
            # Sleep for just a little to yield for other threads
            if oppleoConfig.appSocketIO is not None:
                oppleoConfig.appSocketIO.sleep(0.05)
            else:
                time.sleep(0.05)

