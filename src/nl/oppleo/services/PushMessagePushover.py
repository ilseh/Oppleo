import logging
import requests

from nl.oppleo.config.OppleoSystemConfig import OppleoSystemConfig

oppleoSystemConfig = OppleoSystemConfig()

class PushMessagePushover(object):
    __logger = logging.getLogger('nl.oppleo.services.PushMessagePushover')

    __API_BASE = "https://pushover.net/api"

    HTTP_200_OK = 200

    priorityVeryLow = -2
    priorityModerate = -1
    priorityNormal = 0
    priorityHigh = 1
    priorityEmergency = 2

    @staticmethod
    def sendMessage(title=None, message='', priority=priorityNormal, apiKey='', userKey='', chargerName='Unknown', device=None, sound=None):

        if PushMessagePushover.__logger is None:
            PushMessagePushover.__logger = logging.getLogger('nl.oppleo.services.PushMessagePushover')
        PushMessagePushover.__logger.debug("sendMessage()")

        data = {
            'token'         : apiKey,
            'user'          : userKey,
            'message'       : message,
            'priority'      : priority
        }
        if title is not None:
            data['title'] = title
        else:
            data['title'] = str('Oppleo' + ' ' + chargerName)
        if device is not None:
            data['device'] = device
        if sound is not None:
            data['sound'] = device
        try:
            r = requests.post(
                url     = PushMessagePushover.__API_BASE,
                headers = {
                            'Content-Type': 'application/x-www-form-urlencoded'
                            },
                data    = data,
                timeout = oppleoSystemConfig.httpTimeout
            )
            PushMessagePushover.__logger.debug("Result {} - {} ".format(r.status_code, r.reason))
            if r.status_code != PushMessagePushover.HTTP_200_OK:
                PushMessagePushover.__logger.warn("PushMessagePushover.sendMessage(): status code {} not Ok!".format(r.status_code))

        except requests.exceptions.ConnectTimeout as ct:
            PushMessagePushover.__logger.warn("PushMessagePushover.sendMessage(): ConnectTimeout (>{}s)".format(oppleoSystemConfig.httpTimeout))
        except requests.ReadTimeout as rt:
            PushMessagePushover.__logger.warn("PushMessagePushover.sendMessage(): ReadTimeout (>{}s)".format(oppleoSystemConfig.httpTimeout))
        except Exception as e:
            PushMessagePushover.__logger.warn("PushMessagePushover.sendMessage(): Exception {} not Ok!".format(e))

