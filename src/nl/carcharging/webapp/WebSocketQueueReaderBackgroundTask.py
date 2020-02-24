import logging
import threading
import time

""" 
  As Flask uses it's own socketio implementation, which allows emit only from the main Thread or greenlet threads
  started as background task, this is a greenlet thread background task reading from a queue and emitting messages
  to web sockets
"""

class WebSocketQueueReaderBackgroundTask(object):
    # Count the message updates send through the websocket
    counter = 0
    most_recent = ""
    appSocketIO = None
    wsEmitQueue = None
    stop_event = None

    def __init__(self):
        self.logger = logging.getLogger('nl.carcharging.webapp.WebSocketQueueReaderBackgroundTask')
        self.thread = None
        self.stop_event = threading.Event()

    def stop(self):
        self.logger.debug('Requested to stop')
        self.stop_event.set()

    def websocket_start(self):
        global WebAppConfig
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
                # self.appSocketIO.emit('status_update', { 'data': 'whatever' }, namespace='/usage')
                # self.appSocketIO.emit('status_update1', { 'data': msg['data'] }, namespace='/usage')
                m_body = {}
                if 'data' in msg and msg['data'] is not None:
                    m_body['data'] = msg['data']
                if 'id' in msg and  msg['id'] is not None:
                    m_body['id'] = msg['id']
                if 'status' in msg and  msg['status'] is not None:
                    m_body['status'] = msg['status']
                self.appSocketIO.emit(
                        msg['event'],
                        m_body,
                        namespace=msg['namespace']
                    )
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
