import logging

from nl.oppleo.config.OppleoConfig import OppleoConfig
from nl.oppleo.services.PushMessageProwl import PushMessageProwl


class PushMessage(object):
    logger = logging.getLogger('nl.oppleo.services.PushMessage')

    priorityVeryLow = -2
    priorityModerate = -1
    priorityNormal = 0
    priorityHigh = 1
    priorityEmergency = 2

    @staticmethod
    def sendMessage(title, message, priority=priorityNormal):
        global OppleoConfig

        PushMessage.logger.debug("sendMessage()")
        if OppleoConfig.prowlEnabled:
            PushMessageProwl.sendMessage(title, message, priority)

