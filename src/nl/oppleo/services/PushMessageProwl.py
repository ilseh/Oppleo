
import logging
import requests

from nl.oppleo.config.OppleoConfig import OppleoConfig


class PushMessageProwl(object):
    logger = logging.getLogger('nl.oppleo.services.PushMessageProwl')

    API_BASE = "https://api.prowlapp.com/publicapi/add"

    HTTP_200_OK = 200

    priorityVeryLow = -2
    priorityModerate = -1
    priorityNormal = 0
    priorityHigh = 1
    priorityEmergency = 2

    @staticmethod
    def sendMessage(title, message, priority=priorityNormal):
        global OppleoConfig
        if PushMessageProwl.logger is None:
            logger = logging.getLogger('nl.oppleo.services.PushMessageProwl')
        PushMessageProwl.logger.debug("sendMessage()")
        """
        url = "apikey=4198c61d70f8242bd9e2cba22f87dff9db95f2d4&application=HomeSeer&priority=" & priority & "&event=" & mTitle & "&description=" & mMessage
        url_response = hs.URLAction("https://api.prowlapp.com/publicapi/add", "POST", url, "Content-Type: application/x-www-form-urlencoded")  
        """
        data = {
            'apikey'        : OppleoConfig.prowlApiKey,
            'priority'      : priority,
            'application'   : str('Oppleo' + ' ' + OppleoConfig.ENERGY_DEVICE_ID),
            'event'         : title,
            'description'   : message
        }
        r = requests.post(
            url = PushMessageProwl.API_BASE,
            headers= {
                'Content-Type': 'application/x-www-form-urlencoded'
                },
            data = data
        )
        PushMessageProwl.logger.debug("Result {} - {} ".format(r.status_code, r.reason))
        if r.status_code != PushMessageProwl.HTTP_200_OK:
            PushMessageProwl.logger.warn("PushMessageProwl.sendMessage(): status code {} not Ok!".format(r.status_code))


