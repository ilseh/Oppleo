    
import logging

from src.nl.carcharging.config.WebAppConfig import WebAppConfig


class WebSocketUtil(object):
    logger = logging.getLogger('nl.carcharging.utils.WebSocketUtil')

    @staticmethod
    def emit(event, data, namespace='/'):
        global WebAppConfig

        if WebAppConfig.wsEmitQueue is not None:
            WebSocketUtil.logger.debug(f'Submit msg to websocket emit queue ... {msg}')

            msg = {}
            msg['event'] = event
            msg['data'] = data
            msg['namespace'] = namespace
            WebAppConfig.wsEmitQueue.put(msg)
        else:
            WebSocketUtil.logger.debug('Websocket emit queue not instantiated')
