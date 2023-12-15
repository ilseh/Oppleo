import sys
import threading
import time
import logging
from datetime import datetime, timedelta

from nl.oppleo.exceptions.Exceptions import (NotAuthorizedException, 
                                             OtherRfidHasOpenSessionException, 
                                             ExpiredException)

from nl.oppleo.config.OppleoSystemConfig import OppleoSystemConfig
from nl.oppleo.config.OppleoConfig import OppleoConfig



oppleoSystemConfig = OppleoSystemConfig()
oppleoConfig = OppleoConfig()

 
class MqttHandlerThread(object):
    threadLock = None
    appSocketIO = None
    logger = None
    __mqtt_handler_thread = None
    stop_event = None
    counter = 0

    def __init__(self):
        self.threadLock = threading.Lock()
        self.logger = logging.getLogger('nl.oppleo.daemon.MqttHandlerThread')
        self.__mqtt_handler_thread = None
        self.stop_event = threading.Event()


    def start(self):
        self.stop_event.clear()
        self.logger.debug('Launching Thread...')

        self.logger.debug('.start() - start MqttHandlerThread')
        self.__mqtt_handler_thread = threading.Thread(target=self.mqttReaderLoop, name='MqttHandlerThread')
        self.__mqtt_handler_thread.start()

        self.logger.debug('.start() - Done starting MqttHandlerThread background tasks')


    # __mqtt_handler_thread
    def mqttReaderLoop(self):
        global oppleoConfig

        while not self.stop_event.is_set():

            # TODO
            # - read MQTT, check for WILL messages

            # Sleep to allow other threads
            # time.sleep(0.25)
            time.sleep(0.75)


    def stop(self, block=False):
        self.logger.debug('.stop() - Requested to stop')
        self.stop_event.set()
        if self.__mqtt_handler_thread is not None:
            self.__mqtt_handler_thread.stop()

