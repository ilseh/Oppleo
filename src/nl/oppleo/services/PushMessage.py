import logging

from nl.oppleo.config.OppleoSystemConfig import OppleoSystemConfig
from nl.oppleo.config.OppleoConfig import OppleoConfig
from nl.oppleo.services.PushMessageProwl import PushMessageProwl

oppleoSystemConfig = OppleoSystemConfig()
oppleoConfig = OppleoConfig()

class PushMessage(object):
    logger = logging.getLogger('nl.oppleo.services.PushMessage')

    priorityVeryLow = -2
    priorityModerate = -1
    priorityNormal = 0
    priorityHigh = 1
    priorityEmergency = 2

    @staticmethod
    def sendMessage(title, message, priority=priorityNormal):
        global oppleoConfig

        PushMessage.logger.debug("sendMessage()")
        if oppleoSystemConfig.prowlEnabled:
            PushMessageProwl.sendMessage(
                    title=title, 
                    message=message, 
                    priority=priority, 
                    apiKey=oppleoSystemConfig.prowlApiKey, 
                    chargerName=oppleoConfig.chargerName
                    )

