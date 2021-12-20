import logging
import requests

from nl.oppleo.config.OppleoSystemConfig import OppleoSystemConfig

oppleoSystemConfig = OppleoSystemConfig()

class PushMessageProwl(object):
    __logger = logging.getLogger('nl.oppleo.services.PushMessageProwl')

    __API_BASE = "https://api.prowlapp.com/publicapi/add"

    HTTP_200_OK = 200

    priorityVeryLow = -2
    priorityModerate = -1
    priorityNormal = 0
    priorityHigh = 1
    priorityEmergency = 2

    @staticmethod
    def sendMessage(title, message, priority=priorityNormal, apiKey='', chargerName='Unknown') -> bool:

        if PushMessageProwl.__logger is None:
            PushMessageProwl.__logger = logging.getLogger('nl.oppleo.services.PushMessageProwl')
        PushMessageProwl.__logger.debug("sendMessage()")

        data = {
            'apikey'        : apiKey,
            'priority'      : priority,
            'application'   : str('Oppleo' + ' ' + chargerName),
            'event'         : title,
            'description'   : message
        }
        try:
            r = requests.post(
                url     = PushMessageProwl.__API_BASE,
                headers = {
                            'Content-Type': 'application/x-www-form-urlencoded'
                            },
                data    = data,
                timeout = oppleoSystemConfig.httpTimeout
            )
            PushMessageProwl.__logger.debug("Result {} - {} ".format(r.status_code, r.reason))
            if r.status_code != PushMessageProwl.HTTP_200_OK:
                PushMessageProwl.__logger.warn("PushMessageProwl.sendMessage(): status code {} not Ok!".format(r.status_code))

        except requests.exceptions.ConnectTimeout as ct:
            PushMessageProwl.__logger.warn("PushMessageProwl.sendMessage(): ConnectTimeout (>{}s)".format(oppleoSystemConfig.httpTimeout))
            return False
        except requests.ReadTimeout as rt:
            PushMessageProwl.__logger.warn("PushMessageProwl.sendMessage(): ReadTimeout (>{}s)".format(oppleoSystemConfig.httpTimeout))
            return False
        except Exception as e:
            PushMessageProwl.__logger.warn("PushMessageProwl.sendMessage(): Exception {} not Ok!".format(e))
            return False

        return True