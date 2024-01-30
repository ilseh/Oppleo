import logging
import requests
import json

from nl.oppleo.config.OppleoSystemConfig import OppleoSystemConfig

oppleoSystemConfig = OppleoSystemConfig()

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class PushMessagePushover(object, metaclass=Singleton):
    __logger = None

    __API_BASE = "https://api.pushover.net/1/messages.json"
    __API_USER_VALIDATION = "https://api.pushover.net/1/users/validate.json"
    __API_SOUNDS_BASE = "https://api.pushover.net/1/sounds.json"

    HTTP_200_OK = 200

    priorityVeryLow = -2
    priorityModerate = -1
    priorityNormal = 0
    priorityHigh = 1
    priorityEmergency = 2


    def __init__(self):
        self.__logger = logging.getLogger(self.__class__.__module__)
        self.__logger.setLevel(level=oppleoSystemConfig.getLogLevelForModule(self.__class__.__module__))   


    def sendMessage(self, title=None, message='', priority=priorityNormal, apiKey='', userKey='', chargerName='Unknown', device=None, sound=None) -> bool:
        self.__logger.debug("sendMessage()")

        data = {
            'token'         : apiKey,
            'user'          : userKey,
            'message'       : message,
            'priority'      : priority
        }
        data['title'] = str(title if title is not None else "") + ' [' + chargerName + ']'
        if device is not None:
            data['device'] = device
        if sound is not None:
            data['sound'] = sound
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
                return False

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


    def userValidation(self, apiKey='', userKey=''):
        try:
            data = {
                'token'         : apiKey,
                'user'          : userKey
            }
            r = requests.post(
                url     = self.__API_USER_VALIDATION,
                headers = {
                            'Content-Type': 'application/x-www-form-urlencoded'
                            },
                data    = data,
                timeout = oppleoSystemConfig.httpTimeout
            )
            self.__logger.debug("Result {} - {} ".format(r.status_code, r.reason))
            if r.status_code == self.HTTP_200_OK:
                self.__logger.info("self.availableSounds(): status code {} Ok".format(r.status_code))
                response_dict = json.loads(r.text)
                return response_dict['sounds']

        except requests.exceptions.ConnectTimeout as ct:
            self.__logger.warn("self.userValidation(): ConnectTimeout (>{}s)".format(oppleoSystemConfig.httpTimeout))
        except requests.ReadTimeout as rt:
            self.__logger.warn("self.userValidation(): ReadTimeout (>{}s)".format(oppleoSystemConfig.httpTimeout))
        except Exception as e:
            self.__logger.warn("self.userValidation(): Exception {} not Ok!".format(e))
    
        return None



    def deviceList(self, userKey='', apiKey=''):
        try:
            data = {
                'token'         : apiKey,
                'user'          : userKey
            }
            r = requests.post(
                url     = self.__API_USER_VALIDATION,
                headers = {
                            'Content-Type': 'application/x-www-form-urlencoded'
                            },
                data    = data,
                timeout = oppleoSystemConfig.httpTimeout
            )
            self.__logger.debug("Result {} - {} ".format(r.status_code, r.reason))
            if r.status_code == self.HTTP_200_OK:
                self.__logger.info("self.deviceList(): status code {} Ok".format(r.status_code))
                response_dict = json.loads(r.text)
                resDict = {}
                for deviceIndex, deviceName in enumerate(response_dict['devices']):
                    resDict[deviceName] = deviceName
                return resDict

        except requests.exceptions.ConnectTimeout as ct:
            self.__logger.warn("self.deviceList(): ConnectTimeout (>{}s)".format(oppleoSystemConfig.httpTimeout))
        except requests.ReadTimeout as rt:
            self.__logger.warn("self.deviceList(): ReadTimeout (>{}s)".format(oppleoSystemConfig.httpTimeout))
        except Exception as e:
            self.__logger.warn("self.deviceList(): Exception {} not Ok!".format(e))
    
        return None


    def availableSounds(self, apiKey=''):
        try:
            r = requests.get(
                url     = self.__API_SOUNDS_BASE + '?token=' + apiKey,
                timeout = oppleoSystemConfig.httpTimeout
            )
            self.__logger.debug("self.availableSounds(): Result {} - {} ".format(r.status_code, r.reason))
            if r.status_code == self.HTTP_200_OK:
                self.__logger.info("self.availableSounds(): status code {} Ok".format(r.status_code))
                response_dict = json.loads(r.text)
                return response_dict['sounds']

        except requests.exceptions.ConnectTimeout as ct:
            self.__logger.warn("self.availableSounds(): ConnectTimeout (>{}s)".format(oppleoSystemConfig.httpTimeout))
        except requests.ReadTimeout as rt:
            self.__logger.warn("self.availableSounds(): ReadTimeout (>{}s)".format(oppleoSystemConfig.httpTimeout))
        except Exception as e:
            self.__logger.warn("self.availableSounds(): Exception {} not Ok!".format(e))
    
        return None

pushMessagePushover = PushMessagePushover()