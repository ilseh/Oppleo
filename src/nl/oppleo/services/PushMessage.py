import logging

from nl.oppleo.config.OppleoConfig import OppleoConfig
from nl.oppleo.services.PushMessageProwl import PushMessageProwl

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
        if oppleoConfig.prowlEnabled:
            PushMessageProwl.sendMessage(
                    title=title, 
                    message=message, 
                    priority=priority, 
                    apiKey=oppleoConfig.prowlApiKey, 
                    chargerName=oppleoConfig.chargerName
                    )

