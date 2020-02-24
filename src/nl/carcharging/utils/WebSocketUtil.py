    
import logging

from nl.carcharging.config.WebAppConfig import WebAppConfig


class WebSocketUtil(object):
    logger = logging.getLogger('nl.carcharging.utils.WebSocketUtil')

    @staticmethod
    def emit(event, data, namespace='/'):
        global WebAppConfig

        if WebAppConfig.wsEmitQueue is not None:
            msg = {}
            msg['event'] = event
            while 'data' in data:
                # Nested, unravel
                data = data['data']
            msg['data'] = data
            msg['namespace'] = namespace
            WebSocketUtil.logger.debug(f'Submit msg to websocket emit queue ... {msg}')
            WebAppConfig.wsEmitQueue.put(msg)
        else:
            WebSocketUtil.logger.debug('Websocket emit queue not instantiated')
