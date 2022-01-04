import logging
import threading
import time
import math

from nl.oppleo.config.OppleoConfig import OppleoConfig

from nl.oppleo.models.EnergyDeviceMeasureModel import EnergyDeviceMeasureModel
from nl.oppleo.utils.OutboundEvent import OutboundEvent


oppleoConfig = OppleoConfig()

DEFAULT_TIME_BETWEEN_EVENTS = 0.01
DEFAULT_TIME_BETWEEN_PAGES = 0.1
DEFAULT_PAGE_SIZE = 20
DEFAULT_UPDATE_INTERVAL = 100

class MqttSendHistoryThread(object):
    __logger = None
    __thread = None
    __stop_event = None
    __page_size = DEFAULT_PAGE_SIZE
    __time_between_pages = DEFAULT_TIME_BETWEEN_PAGES
    __time_between_events = DEFAULT_TIME_BETWEEN_EVENTS
    __update_interval = DEFAULT_UPDATE_INTERVAL
    __time_start = 0
    __time_completed = 0
    __processed = 0
    __total = 0


    def __init__(self, page_size=DEFAULT_PAGE_SIZE, time_between_pages=DEFAULT_TIME_BETWEEN_PAGES, time_between_events=DEFAULT_TIME_BETWEEN_EVENTS, update_interval=DEFAULT_UPDATE_INTERVAL):
        self.__logger = logging.getLogger('nl.oppleo.daemon.MqttSendHistoryThread')
        self.__thread = None
        self.__page_size = page_size
        self.__time_between_pages = time_between_pages
        self.__time_between_events = time_between_events
        self.__update_interval = update_interval
        self.__stop_event = threading.Event()


    def start(self):
        self.__stop_event.clear()
        self.__logger.debug('Launching background task...')
        if (self.__thread is not None and self.__thread.isAlive):
            self.__logger.debug('Thread already running!')
            return False

        self.__logger.debug('start_background_task() - monitorEnergyDeviceLoop')
        self.__time_start = 0
        self.__time_completed = 0
        self.__processed = 0
        self.__total = 0
        #   appSocketIO.start_background_task launches a background_task
        #   This really doesn't do parallelism well, basically runs the whole thread befor it yields...
        #   Therefore use standard threads
        self.__thread = threading.Thread(target=self.__mqttSendHistoryLoop, name='mqttSendHistoryThread')
        self.__thread.start()


    def stop(self):
        self.__logger.debug('Requested to stop')
        self.__stop_event.set()


    @property
    def status(self):
        processingTime = 0 if self.__time_start == 0 else (time.time() - self.__time_start) if self.__time_completed == 0 else (self.__time_completed - self.__time_start)
        return { "total"            : self.__total,
                 "processed"        : self.__processed,
                 "started"          : self.__time_start,
                 "completed"        : (self.__time_completed != 0 and self.__processed == self.__total),
                 "running"          : (self.__time_completed != 0),
                 "processingtime"   : float(round(processingTime, 3))
        }


    def __mqttSendHistoryLoop(self):
        global oppleoConfig
        self.logger.debug('mqttSendHistoryLoop()...')

        self.__time_start = time.time()

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
        lastUpdate = 1

        while not self.stop_event.is_set() and (pageResult is None or pageResult.count() == self.__page_size) and offset < 200:
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
                oppleoConfig.appSocketIO.sleep(self.__time_between_events)
                self.__processed += 1

                if math.trunc(self.__processed / self.__page_size) > lastUpdate:
                    OutboundEvent.triggerEvent(
                        event='mqtt_send_history_update',
                        id=oppleoConfig.chargerName,
                        data=self.status,
                        namespace='/mqtt',
                        public=False
                    )
                    lastUpdate = math.trunc(self.__processed / self.__page_size)

            offset += pageResult.count()
            oppleoConfig.appSocketIO.sleep(self.__time_between_pages)

        self.__time_completed = time.time()

        OutboundEvent.triggerEvent(
            event='mqtt_send_history_completed' if self.__processed == self.__total else 'mqtt_send_history_cancelled', 
            id=oppleoConfig.chargerName,
            data=self.status,
            namespace='/mqtt',
            public=False
        )

        self.logger.debug(f'Terminating thread')
