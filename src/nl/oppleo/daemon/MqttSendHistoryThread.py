import logging
import threading
import time
from enum import IntEnum
import random

from nl.oppleo.config.OppleoSystemConfig import OppleoSystemConfig
from nl.oppleo.config.OppleoConfig import OppleoConfig

from nl.oppleo.models.EnergyDeviceMeasureModel import EnergyDeviceMeasureModel
from nl.oppleo.utils.OutboundEvent import OutboundEvent

oppleoSystemConfig = OppleoSystemConfig()
oppleoConfig = OppleoConfig()

DEFAULT_DELAY_BETWEEN_MQTT_EVENTS = 0.05
DEFAULT_PAGE_SIZE = 950
DEFAULT_TIME_BETWEEN_FRONT_END_UPDATES = 5 # number of seconds passed

class MqttSendHistoryThreadMode(IntEnum):
    MODE_ONE = 1    # Only batch, uses sqlalchemy ORM pagination
    MODE_TWO = 2    # Only batch, uses sqlalchemy core fetchmany


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
    __delay_between_mqtt_events = DEFAULT_DELAY_BETWEEN_MQTT_EVENTS
    __time_between_front_end_updates = DEFAULT_TIME_BETWEEN_FRONT_END_UPDATES
    __status = Status.INITIAL
    __processingTime = 0
    __processed = 0
    __total = 0
    __front_end_updates = 0
    __mqtt_events = 0
    __current_tps = 0
    __mode = MqttSendHistoryThreadMode.MODE_TWO


    def __init__(self, 
                 page_size=DEFAULT_PAGE_SIZE, 
                 delay_between_mqtt_events=DEFAULT_DELAY_BETWEEN_MQTT_EVENTS, 
                 time_between_front_end_updates=DEFAULT_TIME_BETWEEN_FRONT_END_UPDATES,
                 mode=MqttSendHistoryThreadMode.MODE_TWO):
        self.__logger = logging.getLogger(__name__)
        self.__logger.setLevel(level=oppleoSystemConfig.getLogLevelForModule(__name__))        
        self.__thread = None
        self.__status = Status.INITIAL
        self.__threadLock = threading.Lock()        
        self.__page_size = page_size + random.randrange(101)
        self.__delay_between_mqtt_events = delay_between_mqtt_events
        self.__time_between_front_end_updates = time_between_front_end_updates
        self.__mode = mode
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
                self.__mqtt_events = 0
                self.__total = 0
                #   appSocketIO.start_background_task launches a background_task
                #   This really doesn't do parallelism well, basically runs the whole thread befor it yields...
                #   Therefore use standard threads
                if self.__mode == MqttSendHistoryThreadMode.MODE_ONE:
                    self.__thread = threading.Thread(target=self.__mqttSendHistoryLoopMode1, name='mqttSendHistoryThread')
                else:
                    self.__thread = threading.Thread(target=self.__mqttSendHistoryLoopMode2, name='mqttSendHistoryThread')
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

    def __settings(self):
        return { "batchProcessing"             : True,
                 "batchSize"                   : self.__page_size,
                 "timeBetweenFrontEndUpdates"  : self.__time_between_front_end_updates,
                 "delayBetweenMqttMessages"    : self.__delay_between_mqtt_events
                }
        

    @property
    def status(self):
        #with self.__threadLock:
            if self.__status in [ Status.INITIAL ]:
                return { "process"          : StatusStr[self.__status],
                         "settings"         : self.__settings()
                       }
            if self.__status in [ Status.STARTED, Status.PAUSED ]:
                if self.__processed > 0:
                    return { "process"          : StatusStr[self.__status],
                             "settings"         : self.__settings(),
                             "total"            : self.__total,
                             "processed"        : self.__processed,
                             "mqttMessages"     : self.__mqtt_events,
                             "frontEndUpdates"  : self.__front_end_updates,
                             "mqttEvents"       : self.__mqtt_events,
                             "remaining"        : ( self.__total - self.__processed ),
                             "processingtime"   : float(round(self.__processingTime, 3)),
                             "tps"              : int(self.__processed / self.__processingTime),
                             "currentTps"       : self.__current_tps if (self.__status in [ Status.STARTED ]) else 0,
                             "timeestimation"   : float(round((( self.__processingTime / self.__processed ) * self.__total ), 3)),
                             "timeremaining"    : float(round((( self.__processingTime / self.__processed ) * ( self.__total - self.__processed )), 3))
                    }
                else:
                    return { "process"          : StatusStr[self.__status],
                             "settings"         : self.__settings(),
                             "total"            : self.__total,
                             "processed"        : self.__processed,
                             "mqttEvents"       : self.__mqtt_events,
                             "frontEndUpdates"  : self.__front_end_updates,
                             "remaining"        : ( self.__total - self.__processed ),
                             "processingtime"   : float(round(self.__processingTime, 3)),
                             "tps"              : 0,
                             "currentTps"       : 0

                    }
            if self.__status in [ Status.COMPLETED, Status.CANCELLED ]:
                return { "process"          : StatusStr[self.__status],
                         "settings"         : self.__settings(),
                         "total"            : self.__total,
                         "processed"        : self.__processed,
                         "mqttEvents"       : self.__mqtt_events,
                         "frontEndUpdates"  : self.__front_end_updates,
                         "processingtime"   : float(round(self.__processingTime, 3)),
                         "tps"              : int(self.__processed / self.__processingTime),
                         "currentTps"       : 0
                }

 
    @property
    def statusId(self) -> int:
        with self.__threadLock:
            return self.__status

    @property
    def mode(self):
        with self.__threadLock:
            return self.__mode

    @mode.setter
    def mode(self, mode:int=MqttSendHistoryThreadMode.MODE_TWO):
        with self.__threadLock:
            self.__mode = mode

    def __sendMqttEventIfTime(self):
        if len(self.__batch) > self.__page_size:
            pass

    # Runs on each entry
    def __mqttResultSetHandler(self, resultSet=None) -> bool:
        # Build batch
        for entryResult in resultSet:
            self.__batch.append(EnergyDeviceMeasureModel.sto_str(entryResult))
        # Time to send it out. Send MQTT event as batch (Array)
        OutboundEvent.emitMQTTEvent( event='status_update',
                                        data=self.__batch,
                                        status=None,
                                        id=None,
                                        namespace='/usage')
        # Now assign an new array. Don't empty with .clear() as the emitting function could still be working on the old one.
        self.__batch = []
        self.__mqtt_events += 1

        self.__processed += len(resultSet)

        intermediate_timestamp = time.time()
        self.__processingTime += (intermediate_timestamp - self.__time_start)
        self.__current_tps = int(len(resultSet) / (intermediate_timestamp - self.__time_start))
        self.__time_start = intermediate_timestamp

        if (time.time() - self.__lastUpdate) > self.__time_between_front_end_updates:
            OutboundEvent.triggerEvent(
                event='mqtt_send_history_update',
                id=oppleoConfig.chargerID,
                data=self.status,
                namespace='/mqtt',
                public=False
            )
            self.__front_end_updates += 1
            self.__lastUpdate = time.time()

        time.sleep(self.__delay_between_mqtt_events)

        if self.__pause_event.is_set():
            # pause
            self.__status = Status.PAUSED
            self.__current_tps = 0
            OutboundEvent.triggerEvent(
                event='mqtt_send_history_paused',
                id=oppleoConfig.chargerID,
                data=self.status,
                namespace='/mqtt',
                public=False
            )
            while self.__pause_event.is_set() and not self.__cancel_event.is_set():
                self.__time_start = time.time()
                time.sleep(self.__delay_between_mqtt_events)
            if not self.__cancel_event.is_set():
                self.__status = Status.STARTED
                OutboundEvent.triggerEvent(
                    event='mqtt_send_history_started',
                    id=oppleoConfig.chargerID,
                    data=self.status,
                    namespace='/mqtt',
                    public=False
                )
        if self.__cancel_event.is_set():
            # End it here
            return False
        
        return True


    # The main loop (2)
    def __mqttSendHistoryLoopMode2(self):
        self.__logger.debug('mqttSendHistoryLoop()...')

        self.__processingTime = 0
        self.__current_tps = 0
        self.__time_start = time.time()

        edmm = EnergyDeviceMeasureModel()
        edmm.energy_device_id = oppleoConfig.energyDevice

        self.__total = edmm.get_count()

        OutboundEvent.triggerEvent(
                    event='mqtt_send_history_started', 
                    id=oppleoConfig.chargerID,
                    data=self.status,
                    namespace='/mqtt',
                    public=False
                )

        self.__lastUpdate = self.__time_start

        self.__batch = []
        edmm = EnergyDeviceMeasureModel()

        # Run them all
        edmm.get_all_as_stream(self.__mqttResultSetHandler, self.__page_size)

        # Finished or cancelled
        self.__status = Status.COMPLETED if not self.__cancel_event.is_set() else Status.CANCELLED
        self.__processingTime += (time.time() - self.__time_start)
        OutboundEvent.triggerEvent(
            event='mqtt_send_history_completed' if self.__status == Status.COMPLETED else 'mqtt_send_history_cancelled', 
            id=oppleoConfig.chargerID,
            data=self.status,
            namespace='/mqtt',
            public=False
        )

        self.__logger.debug(f'Terminating thread')
        self.__thread = None




    def __mqttSendHistoryLoopMode1(self):
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
                    id=oppleoConfig.chargerID,
                    data=self.status,
                    namespace='/mqtt',
                    public=False
                )

        offset = 0
        pageResult = None
        lastUpdate = time_start

        while not self.__cancel_event.is_set() and (pageResult is None or pageResult.count() == self.__page_size):
            pageResult = edmm.paginate(energy_device_id = oppleoConfig.chargerID,
                                       offset           = offset, 
                                       limit            = self.__page_size, 
                                       orderColumn      = getattr(EnergyDeviceMeasureModel, 'created_at'),
                                       orderDir         = 'desc'
                                    )
            batch = []
            for entryResult in pageResult:
                # Build batch
                batch.append(entryResult.to_str())
            # Send MQTT event as batch (Array)
            OutboundEvent.emitMQTTEvent( event='status_update',
                                            data=batch,
                                            status=None,
                                            id=None,
                                            namespace='/usage')
            self.__processed += pageResult.count()
            self.__mqtt_events += 1
            time.sleep(self.__delay_between_mqtt_events)

            intermediate_timestamp = time.time()
            self.__processingTime += (intermediate_timestamp - time_start)
            self.__current_tps = int(pageResult.count() / (intermediate_timestamp - time_start))
            time_start = intermediate_timestamp

            if (time.time() - lastUpdate) > self.__time_between_front_end_updates:
                OutboundEvent.triggerEvent(
                    event='mqtt_send_history_update',
                    id=oppleoConfig.chargerID,
                    data=self.status,
                    namespace='/mqtt',
                    public=False
                )
                self.__front_end_updates += 1
                lastUpdate = time.time()

            if self.__pause_event.is_set():
                self.__status = Status.PAUSED
                self.__current_tps = 0
                OutboundEvent.triggerEvent(
                    event='mqtt_send_history_paused',
                    id=oppleoConfig.chargerID,
                    data=self.status,
                    namespace='/mqtt',
                    public=False
                )
                while self.__pause_event.is_set() and not self.__cancel_event.is_set():
                    time_start = time.time()
                    time.sleep(self.__delay_between_mqtt_events)
                if not self.__cancel_event.is_set():
                    self.__status = Status.STARTED
                    OutboundEvent.triggerEvent(
                        event='mqtt_send_history_started',
                        id=oppleoConfig.chargerID,
                        data=self.status,
                        namespace='/mqtt',
                        public=False
                    )

            offset += pageResult.count()

        self.__status = Status.COMPLETED if not self.__cancel_event.is_set() else Status.CANCELLED
        self.__processingTime += (time.time() - time_start)
        OutboundEvent.triggerEvent(
            event='mqtt_send_history_completed' if self.__status == Status.COMPLETED else 'mqtt_send_history_cancelled', 
            id=oppleoConfig.chargerID,
            data=self.status,
            namespace='/mqtt',
            public=False
        )

        self.__logger.debug(f'Terminating thread')
        self.__thread = None
