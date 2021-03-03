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
    def sendMessage(title, message, priority=priorityNormal, apiKey='', chargerName='Unknown'):

        if PushMessageProwl.__logger is None:
            PushMessageProwl.__logger = logging.getLogger('nl.oppleo.services.PushMessageProwl')
        PushMessageProwl.__logger.debug("sendMessage()")
        """
        url = "apikey=4198c61d70f8242bd9e2cba22f87dff9db95f2d4&application=HomeSeer&priority=" & priority & "&event=" & mTitle & "&description=" & mMessage
        url_response = hs.URLAction("https://api.prowlapp.com/publicapi/add", "POST", url, "Content-Type: application/x-www-form-urlencoded")  
        """
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
        except Exception as e:
            PushMessageProwl.__logger.warn("PushMessageProwl.sendMessage(): Exception {} not Ok!".format(e))

