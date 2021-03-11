import logging
import threading
import time

from nl.oppleo.config.OppleoConfig import OppleoConfig

""" 
  As Flask uses it's own socketio implementation, which allows emit only from the main Thread or greenlet threads
  started as background task, this is a greenlet thread background task reading from a queue and emitting messages
  to web sockets
"""

oppleoConfig = OppleoConfig()

class WebSocketQueueReaderBackgroundTask(object):
    # Count the message updates send through the websocket
    counter = 0
    most_recent = ""
    appSocketIO = None
    wsEmitQueue = None
    stop_event = None

    def __init__(self):
        self.logger = logging.getLogger('nl.oppleo.webapp.WebSocketQueueReaderBackgroundTask')
        self.thread = None
        self.stop_event = threading.Event()

    def stop(self):
        self.logger.debug('Requested to stop')
        self.stop_event.set()

    def websocket_start(self):
        global oppleoConfig
        self.logger.debug('Starting background task...')
        while not self.stop_event.is_set():
            # Sleep is interruptable by other threads, so sleep for 0.1 seconds, then check passed time

            if not self.wsEmitQueue.empty():
                # Blocking call, make sure there is a message to obtain
                msg = self.wsEmitQueue.get()
                """
                msg is a dict object with event, data, and namespace
                """
                # Emit as web socket update
                self.counter += 1
                self.logger.debug(f'Send msg {self.counter} via websocket ...{msg}')
                m_body = {}
                if 'data' in msg and msg['data'] is not None:
                    m_body['data'] = msg['data']
                if 'id' in msg and  msg['id'] is not None:
                    m_body['id'] = msg['id']
                if 'status' in msg and  msg['status'] is not None:
                    m_body['status'] = msg['status']
                if ('public' in msg and msg['public']):
                    self.appSocketIO.emit(
                            event=msg['event'],
                            data=m_body,
                            namespace=msg['namespace']
                        )
                else:
                    """
                        Private message
                        - Emit only to recipient or to all authenticated clients
                        - room is the request.sid of the specific client
                    """
                    if ('room' in msg and msg['room'] is not None):
                        # Emit only to a specific room, or recipient (sid)
                        self.appSocketIO.emit(
                                event=msg['event'],
                                data=m_body,
                                namespace=msg['namespace'],
                                room=msg['room']
                                )
                    else:
                        # Emit to authenticated clients
                        # room is the request.sid of the specific client
                        # connectedClients can change at any time. Iterating can cause issues. list() creates a copy of the keys
                        for sid in list(oppleoConfig.connectedClients):
                            # oppleoConfig.connectedClients[sid] raises KeyError is key does not exist. Get does not.
                            connectedClient = oppleoConfig.connectedClients.get(sid, None)
                            if connectedClient is None:
                                # pass this sid, no longer connected
                                continue
                            if 'auth' in connectedClient and connectedClient['auth']:
                                # Authenticated client, emit data
                                self.logger.debug('Sending msg {} via websocket to {}...'.format(msg, connectedClient['sid']))
                                self.appSocketIO.emit(
                                        event=msg['event'],
                                        data=m_body,
                                        namespace=msg['namespace'],
                                        room=connectedClient['sid']
                                        )
                            else:
                                self.logger.debug('NOT sending msg {} via websocket to {}...'.format(msg, connectedClient['sid']))


                self.wsEmitQueue.task_done()
            self.appSocketIO.sleep(0.5)

        self.logger.debug(f'Terminating thread')
        # Releasing session if applicable


    def start(self, appSocketIO, wsEmitQueue):
        self.stop_event.clear()
        self.logger.debug('Launching background task...')
        self.appSocketIO = appSocketIO
        self.wsEmitQueue = wsEmitQueue
        self.thread = self.appSocketIO.start_background_task(self.websocket_start)


    def wait(self):
        self.thread.join()
