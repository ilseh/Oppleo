import logging

from nl.carcharging.config.WebAppConfig import WebAppConfig
from nl.carcharging.services.PushMessageProwl import PushMessageProwl


class PushMessage(object):
    logger = logging.getLogger('nl.carcharging.services.PushMessage')

    priorityVeryLow = -2
    priorityModerate = -1
    priorityNormal = 0
    priorityHigh = 1
    priorityEmergency = 2

    @staticmethod
    def sendMessage(title, message, priority=priorityNormal):
        global WebAppConfig

        PushMessage.logger.debug("sendMessage()")
        if WebAppConfig.prowlEnabled:
            PushMessageProwl.sendMessage(title, message, priority)

