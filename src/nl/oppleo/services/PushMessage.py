import logging

from nl.oppleo.config.OppleoSystemConfig import OppleoSystemConfig
from nl.oppleo.config.OppleoConfig import OppleoConfig
from nl.oppleo.services.PushMessageProwl import PushMessageProwl
from nl.oppleo.services.PushMessagePushover import PushMessagePushover

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
                    priority=PushMessage.__mapPriorityToProwl(priority), 
                    apiKey=oppleoSystemConfig.prowlApiKey, 
                    chargerName=oppleoConfig.chargerName
                    )

        if oppleoSystemConfig.pushoverEnabled:
            PushMessagePushover.sendMessage(
                    title=title, 
                    message=message, 
                    priority=PushMessage.__mapPriorityToPushover(priority), 
                    apiKey=oppleoSystemConfig.pushoverApiKey, 
                    userKey=oppleoSystemConfig.pushoverUserKey,
                    device=oppleoSystemConfig.pushoverDevice,
                    sound=oppleoSystemConfig.pushoverSound,
                    chargerName=oppleoConfig.chargerName
                    )


    @staticmethod
    def __mapPriorityToProwl(priority:int=None):
        if priority is None:
            return PushMessageProwl.priorityNormal
        if priority <= -2:
            return PushMessageProwl.priorityVeryLow
        if priority == -1:
            return PushMessageProwl.priorityLow
        if priority >= 2:
            return PushMessageProwl.priorityVeryHigh
        if priority == 1:
            return PushMessageProwl.priorityHigh
        return PushMessageProwl.priorityNormal

    @staticmethod
    def __mapPriorityToPushover(priority:int=None):
        if priority is None:
            return PushMessagePushover.priorityNormal
        if priority <= -2:
            return PushMessagePushover.priorityVeryLow
        if priority == -1:
            return PushMessagePushover.priorityLow
        if priority >= 2:
            return PushMessagePushover.priorityVeryHigh
        if priority == 1:
            return PushMessagePushover.priorityHigh
        return PushMessagePushover.priorityNormal


 def sendMessage(title=None, message='', priority=priorityNormal, apiKey='', userKey='', chargerName='Unknown', device=None, sound=None):