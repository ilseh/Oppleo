import logging

from nl.oppleo.config.OppleoSystemConfig import OppleoSystemConfig
from nl.oppleo.config.OppleoConfig import OppleoConfig

from nl.oppleo.services.PushMessageProwl import pushMessageProwl
from nl.oppleo.services.PushMessagePushover import pushMessagePushover

from nl.oppleo.services.OppleoMqttClient import OppleoMqttClient 

oppleoSystemConfig = OppleoSystemConfig()
oppleoConfig = OppleoConfig()

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class PushMessage(object, metaclass=Singleton):

    __logger = None

    priorityVeryLow = -2
    priorityModerate = -1
    priorityNormal = 0
    priorityHigh = 1
    priorityEmergency = 2

    def __init__(self):
        self.__logger = logging.getLogger(__name__)
        self.__logger.setLevel(level=oppleoSystemConfig.getLogLevelForModule(__name__))   

    def sendMessage(self, title, message, priority=priorityNormal):
        global oppleoConfig

        self.__logger.debug("sendMessage()")
        if oppleoSystemConfig.prowlEnabled:
            pushMessageProwl.sendMessage(
                    title=title, 
                    message=message, 
                    priority=self.__mapPriorityToProwl(priority), 
                    apiKey=oppleoSystemConfig.prowlApiKey, 
                    chargerName=oppleoConfig.chargerNameText
                    )

        if oppleoSystemConfig.pushoverEnabled:
            pushMessagePushover.sendMessage(
                    title=title, 
                    message=message, 
                    priority=self.__mapPriorityToPushover(priority), 
                    apiKey=oppleoSystemConfig.pushoverApiKey, 
                    userKey=oppleoSystemConfig.pushoverUserKey,
                    device=oppleoSystemConfig.pushoverDevice,
                    sound=oppleoSystemConfig.pushoverSound,
                    chargerName=oppleoConfig.chargerNameText
                    )

        if oppleoSystemConfig.mqttOutboundEnabled:
            oppleoMqttClient = OppleoMqttClient()
            topic = 'oppleo/' + oppleoSystemConfig.chargerID + '/notification'
            msg = {}
            if title is not None:
                msg['title'] = title
            if message is not None:
                msg['message'] = message
            if priority is not None:
                msg['priority'] = priority

            self.__logger.debug(f'Submit msg {msg} to MQTT topic {topic} ...')
            try:
                oppleoMqttClient.publish(topic=topic, message=msg)
            except Exception as e:
                self.__logger.error('MQTT server enabled but not reachable! {}'.format(str(e)))


    def __mapPriorityToProwl(self, priority:int=None):
        if priority is None:
            return pushMessageProwl.priorityNormal
        if priority <= -2:
            return pushMessageProwl.priorityVeryLow
        if priority == -1:
            return pushMessageProwl.priorityLow
        if priority >= 2:
            return pushMessageProwl.priorityVeryHigh
        if priority == 1:
            return pushMessageProwl.priorityHigh
        return pushMessageProwl.priorityNormal


    def __mapPriorityToPushover(self, priority:int=None):
        if priority is None:
            return pushMessagePushover.priorityNormal
        if priority <= -2:
            return pushMessagePushover.priorityVeryLow
        if priority == -1:
            return pushMessagePushover.priorityLow
        if priority >= 2:
            return pushMessagePushover.priorityVeryHigh
        if priority == 1:
            return pushMessagePushover.priorityHigh
        return pushMessagePushover.priorityNormal


pushMessage = PushMessage()
