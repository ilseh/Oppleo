import logging
import requests

from nl.oppleo.config.OppleoSystemConfig import OppleoSystemConfig

oppleoSystemConfig = OppleoSystemConfig()

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class PushMessageProwl(object, metaclass=Singleton):
    __logger = None

    __API_BASE = "https://api.prowlapp.com/publicapi/add"

    HTTP_200_OK = 200

    priorityVeryLow = -2
    priorityModerate = -1
    priorityNormal = 0
    priorityHigh = 1
    priorityEmergency = 2

    def __init__(self):
        self.__logger = logging.getLogger(__name__)
        self.__logger.setLevel(level=oppleoSystemConfig.getLogLevelForModule(__name__))   


    def sendMessage(self, title, message, priority=priorityNormal, apiKey='', chargerName='Unknown') -> bool:

        self.__logger.debug("sendMessage()")

        data = {
            'apikey'        : apiKey,
            'priority'      : priority,
            'application'   : str('Oppleo' + ' ' + chargerName),
            'event'         : title,
            'description'   : message
        }
        try:
            r = requests.post(
                url     = self.__API_BASE,
                headers = {
                            'Content-Type': 'application/x-www-form-urlencoded'
                            },
                data    = data,
                timeout = oppleoSystemConfig.httpTimeout
            )
            self.__logger.debug("Result {} - {} ".format(r.status_code, r.reason))
            if r.status_code != self.HTTP_200_OK:
                self.__logger.warn("self.sendMessage(): status code {} not Ok!".format(r.status_code))

        except requests.exceptions.ConnectTimeout as ct:
            self.__logger.warn("self.sendMessage(): ConnectTimeout (>{}s)".format(oppleoSystemConfig.httpTimeout))
            return False
        except requests.ReadTimeout as rt:
            self.__logger.warn("self.sendMessage(): ReadTimeout (>{}s)".format(oppleoSystemConfig.httpTimeout))
            return False
        except Exception as e:
            self.__logger.warn("self.sendMessage(): Exception {} not Ok!".format(e))
            return False

        return True
    

pushMessageProwl = PushMessageProwl()
