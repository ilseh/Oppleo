    
import logging

from nl.carcharging.config.WebAppConfig import WebAppConfig


class WebSocketUtil(object):
    logger = logging.getLogger('nl.carcharging.utils.WebSocketUtil')

    """ 
      public = When True emits the message and contents to all connected clients. When False only emits to 
               authenticated clients
    """ 
    @staticmethod
    def emit(event='event', data=None, status=None, id=None, namespace=None, public=False):
        global WebAppConfig

        if WebAppConfig.wsEmitQueue is not None:
            msg = {}
            msg['event'] = event
            """
            while 'data' in data:
                # Nested, unravel
                data = data['data']
            """
            if data is not None:
                msg['data'] = data
            if status is not None:
                msg['status'] = status
            if id is not None:
                msg['id'] = id
            msg['namespace'] = namespace
            msg['public'] = public
            WebSocketUtil.logger.debug(f'Submit msg to websocket emit queue ... {msg}')
            WebAppConfig.wsEmitQueue.put(msg)
        else:
            WebSocketUtil.logger.debug('Websocket emit queue not instantiated')
