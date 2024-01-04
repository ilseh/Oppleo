import logging
import json

from nl.oppleo.config.OppleoSystemConfig import OppleoSystemConfig
from nl.oppleo.config.OppleoConfig import OppleoConfig
from nl.oppleo.services.EvseReaderProd import EvseReaderProd
from nl.oppleo.services.EvseReaderSimulate import EvseReaderSimulate

oppleoSystemConfig = OppleoSystemConfig()
oppleoConfig = OppleoConfig()

class EvseReader(object):
    logger = None
    reader = None

    def __init__(self):
        self.logger = logging.getLogger('nl.oppleo.service.EvseReader' )
        if oppleoSystemConfig.evseLedReaderEnabled:
            self.logger.debug("Using production Evse reader")
            self.reader = EvseReaderProd()
        else:
            self.logger.debug("Using SIMULATED Evse reader!")
            self.reader = EvseReaderSimulate()

    def loop(self, cb_until, cb_result):
        try:
            self.reader.loop(cb_until, cb_result)
        except Exception as e:
            self.logger.error('Could not start EvseReader loop ({})'.format(str(e)))

    def diag(self):
        return json.dumps({
            "reader_class": "-" if self.reader is None else self.reader.__class__,
            "reader": "-" if self.reader is None else json.loads(self.reader.diag())
            }, 
            default=str     # Overcome "TypeError: Object of type datetime is not JSON serializable"
        )
