import logging
import threading
import time
from enum import IntEnum

from nl.oppleo.config.OppleoConfig import OppleoConfig

from nl.oppleo.models.EnergyDeviceMeasureModel import EnergyDeviceMeasureModel
from nl.oppleo.utils.OutboundEvent import OutboundEvent


oppleoConfig = OppleoConfig()

DEFAULT_DELAY_BETWEEN_EVENTS = 0.05
DEFAULT_PAGE_SIZE = 20
DEFAULT_TIME_BETWEEN_NOTIFICATIONS = 5 # number of seconds passed

"""
    initial -> started (running) -> completed (totals, time)
                                    -> paused (not running, totals, time) -> (re)started running -> completed
                                                                          -> stopped (not running, reset) = not started

"""

class Status(IntEnum):
    INITIAL = 0 
    STARTED = 1  
    PAUSED = 2
    COMPLETED = 3
    CANCELLED = 4

StatusStr = [ 'initial', 'started', 'paused', 'completed', 'cancelled' ]

class MqttSendHistoryThread(object):
    __logger = None
    __thread = None
    __threadLock = None
    __pause_event = None
    __cancel_event = None
    __page_size = DEFAULT_PAGE_SIZE
    __delay_between_events = DEFAULT_DELAY_BETWEEN_EVENTS
    __time_between_notifications = DEFAULT_TIME_BETWEEN_NOTIFICATIONS
    __status = Status.INITIAL
    __processingTime = 0
    __processed = 0
    __total = 0
    __notifications = 0
    __current_tps = 0


    def __init__(self, page_size=DEFAULT_PAGE_SIZE, delay_between_events=DEFAULT_DELAY_BETWEEN_EVENTS, time_between_notifications=DEFAULT_TIME_BETWEEN_NOTIFICATIONS):
        self.__logger = logging.getLogger('nl.oppleo.daemon.MqttSendHistoryThread')
        self.__thread = None
        self.__status = Status.INITIAL
        self.__threadLock = threading.Lock()        
        self.__page_size = page_size
        self.__delay_between_events = delay_between_events
        self.__time_between_notifications = time_between_notifications
        self.__pause_event = threading.Event()
        self.__cancel_event = threading.Event()


    def start(self):
        with self.__threadLock:
            if (self.__status in [ Status.INITIAL, Status.CANCELLED, Status.COMPLETED ]):
                self.__pause_event.clear()
                self.__cancel_event.clear()
                self.__logger.debug('Launching background task...')
                if (self.__thread is not None and self.__thread.isAlive):
                    self.__logger.debug('Thread already running!')
                    return False

                self.__logger.debug('start_background_task() - monitorEnergyDeviceLoop')
                self.__processed = 0
                self.__total = 0
                #   appSocketIO.start_background_task launches a background_task
                #   This really doesn't do parallelism well, basically runs the whole thread befor it yields...
                #   Therefore use standard threads
                self.__thread = threading.Thread(target=self.__mqttSendHistoryLoop, name='mqttSendHistoryThread')
                self.__status = Status.STARTED
                self.__thread.start()
                return { 'success': True, 'message': 'Proces started' }
            if (self.__status in [ Status.PAUSED ]):
                self.__pause_event.clear()
                return { 'success': True, 'message': 'Restart requested' }
            return { 'success': False, 'message': 'Already running' }


    def pause(self):
        self.__logger.debug('Requested to pause')
        with self.__threadLock:
            if (self.__status in [ Status.INITIAL, Status.CANCELLED, Status.COMPLETED ]):
                return { 'success': False, 'message': 'Not running' }
            if (self.__status in [ Status.PAUSED ]):
                return { 'success': False, 'message': 'Already paused' }
            self.__pause_event.set()
            return { 'success': True, 'message': 'Pause requested' }


    def cancel(self):
        self.__logger.debug('Requested to cancel')
        with self.__threadLock:
            if (self.__status in [ Status.INITIAL, Status.CANCELLED, Status.COMPLETED ]):
                return { 'success': False, 'message': 'Not running' }
            self.__cancel_event.set()
            return { 'success': True, 'message': 'Cancel requested' }


    @property
    def status(self):
        #with self.__threadLock:
            if self.__status in [ Status.INITIAL ]:
                return { "process"          : StatusStr[self.__status] }
            if self.__status in [ Status.STARTED, Status.PAUSED ]:
                if self.__processed > 0:
                    return { "process"          : StatusStr[self.__status],
                             "total"            : self.__total,
                             "processed"        : self.__processed,
                             "notifications"    : self.__notifications,
                             "remaining"        : ( self.__total - self.__processed ),
                             "processingtime"   : float(round(self.__processingTime, 3)),
                             "tps"              : int(self.__processed / self.__processingTime),
                             "currentTps"       : self.__current_tps if (self.__status in [ Status.STARTED ]) else 0,
                             "timeestimation"   : float(round((( self.__processingTime / self.__processed ) * self.__total ), 3)),
                             "timeremaining"    : float(round((( self.__processingTime / self.__processed ) * ( self.__total - self.__processed )), 3))
                    }
                else:
                    return { "process"          : StatusStr[self.__status],
                             "total"            : self.__total,
                             "processed"        : self.__processed,
                             "notifications"    : self.__notifications,
                             "remaining"        : ( self.__total - self.__processed ),
                             "processingtime"   : float(round(self.__processingTime, 3)),
                             "tps"              : 0,
                             "currentTps"       : 0

                    }
            if self.__status in [ Status.COMPLETED, Status.CANCELLED ]:
                return { "process"          : StatusStr[self.__status],
                         "total"            : self.__total,
                         "processed"        : self.__processed,
                         "notifications"    : self.__notifications,
                         "processingtime"   : float(round(self.__processingTime, 3)),
                         "tps"              : int(self.__processed / self.__processingTime),
                         "currentTps"       : 0
                }

 
    @property
    def statusId(self) -> int:
        with self.__threadLock:
            return self.__status


    def __mqttSendHistoryLoop(self):
        global oppleoConfig
        self.__logger.debug('mqttSendHistoryLoop()...')

        self.__processingTime = 0
        self.__current_tps = 0
        time_start = time.time()

        edmm = EnergyDeviceMeasureModel()
        edmm.energy_device_id = oppleoConfig.energyDevice

        self.__total = edmm.get_count()

        OutboundEvent.triggerEvent(
                    event='mqtt_send_history_started', 
                    id=oppleoConfig.chargerName,
                    data=self.status,
                    namespace='/mqtt',
                    public=False
                )

        offset = 0
        pageResult = None
        lastUpdate = time_start

        while not self.__cancel_event.is_set() and (pageResult is None or pageResult.count() == self.__page_size):
            pageResult = edmm.paginate(energy_device_id = oppleoConfig.chargerName,
                                       offset           = offset, 
                                       limit            = self.__page_size, 
                                       orderColumn      = getattr(EnergyDeviceMeasureModel, 'created_at'),
                                       orderDir         = 'desc'
                                    )
            for entryResult in pageResult:
                # Send MQTT event
                OutboundEvent.emitMQTTEvent( event='status_update',
                                             data=entryResult.to_str(),
                                             status=None,
                                             id=None,
                                             namespace='/usage')
                time.sleep(self.__delay_between_events)
                self.__processed += 1

                if (time.time() - lastUpdate) > self.__time_between_notifications:
                    OutboundEvent.triggerEvent(
                        event='mqtt_send_history_update',
                        id=oppleoConfig.chargerName,
                        data=self.status,
                        namespace='/mqtt',
                        public=False
                    )
                    self.__notifications += 1
                    lastUpdate = time.time()

            intermediate_timestamp = time.time()
            self.__processingTime += (intermediate_timestamp - time_start)
            time_start = intermediate_timestamp
            self.__current_tps = int(pageResult.count() / (intermediate_timestamp - time_start))


            if self.__pause_event.is_set():
                self.__status = Status.PAUSED
                self.__current_tps = 0
                OutboundEvent.triggerEvent(
                    event='mqtt_send_history_paused',
                    id=oppleoConfig.chargerName,
                    data=self.status,
                    namespace='/mqtt',
                    public=False
                )
                while self.__pause_event.is_set() and not self.__cancel_event.is_set():
                    time_start = time.time()
                    time.sleep(self.__delay_between_events)
                if not self.__cancel_event.is_set():
                    self.__status = Status.STARTED
                    OutboundEvent.triggerEvent(
                        event='mqtt_send_history_started',
                        id=oppleoConfig.chargerName,
                        data=self.status,
                        namespace='/mqtt',
                        public=False
                    )

            offset += pageResult.count()

        self.__status = Status.COMPLETED if self.__processed == self.__total else Status.CANCELLED
        OutboundEvent.triggerEvent(
            event='mqtt_send_history_completed' if self.__processed == self.__total else 'mqtt_send_history_cancelled', 
            id=oppleoConfig.chargerName,
            data=self.status,
            namespace='/mqtt',
            public=False
        )

        self.__logger.debug(f'Terminating thread')

        self.__processingTime += (time.time() - time_start)
        self.__status = Status.COMPLETED if self.__processed == self.__total else Status.CANCELLED
        self.__thread = None

