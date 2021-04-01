import threading
import logging
import time
import re

from nl.oppleo.config.OppleoConfig import OppleoConfig
from nl.oppleo.utils.WebSocketUtil import WebSocketUtil
from nl.oppleo.api.TeslaApi import TeslaAPI
from nl.oppleo.utils.UpdateOdometerTeslaUtil import UpdateOdometerTeslaUtil
from nl.oppleo.utils.TeslaApiFormatters import formatChargeState, formatVehicle
from nl.oppleo.models.RfidModel import RfidModel

oppleoConfig = OppleoConfig()

class VehicleChargeStatusMonitorThread(object):
    __thread = None
    __threadLock = None
    __logger = None
    __stop_event = None

    __rfidTag = None        # The ID string

    # Check every minute [60 seconds]
    __vehicleMonitorInterval = 10
    __sleepInterval = 0.25

    def __init__(self):
        self.__threadLock = threading.Lock()
        self.__stop_event = threading.Event()
        self.__logger = logging.getLogger('nl.oppleo.daemon.VehicleChargeStatusMonitorThread')

    @property
    def rfid(self):
        return self.__rfidTag

    @rfid.setter
    def rfid(self, rfidValue:str=None):
        if self.__thread is not None:
            if self.__thread.is_alive():
                self.__logger.error('Cannot set RFID after Thread is started!')
            else:
                self.__logger.error('Cannot set RFID after Thread is finished!')
            return
        if rfidValue is None:
            self.__logger.error('Cannot set RFID to None!')
        self.__rfidTag = rfidValue


    # VehicleChargeStatusMonitorThread
    """
        This Thread is started when a session is opened (EVSE Enabled), 
        so in this Thread there is no check for an active charge session!
        The RFID Tag is set prior to starting the Thread
        - Creates TeslaAPI 
        - If there is a token, load Token from RFID Tag
        - If the number of Online clients present in list(oppleoConfig.connectedClients) 
            - Get charge state
        - Interval 60 sec (ophalen info kost ~10 sec met TeslaAPI)
        When the session is stopped this Thread is destroyed. With a new session a new Thread is started.
    """
    def monitor(self):
        self.__logger.debug('monitor()')

        teslaApi = TeslaAPI()

        if self.__rfidTag is None:
            self.__logger.error('monitor() Cannot run Thread for RFID None!')

        rfidData = RfidModel.get_one(self.__rfidTag)
        if rfidData is None:
            self.__logger.error('monitor() Cannot run Thread. Cannot get data for RFID {}'.format(self.__rfidTag))

        monitorInterval = 0

        while not self.__stop_event.is_set():
            if monitorInterval > self.__vehicleMonitorInterval:
                monitorInterval = 0
                self.__logger.debug("monitor() loop")
                if len(oppleoConfig.connectedClients) > 0:
                    self.__logger.debug("monitor() connected clients ({})".format(len(oppleoConfig.connectedClients)))
                    # See if something changes (could be added or retracted)
                    UpdateOdometerTeslaUtil.copy_token_from_rfid_model_to_api(rfidData, teslaApi)

                    if teslaApi.hasValidToken():
                        self.__logger.debug("monitor() valid token")

                        # Refresh if required (check once per day)
                        if teslaApi.refreshTokenIfRequired():
                            UpdateOdometerTeslaUtil.copy_token_from_api_to_rfid_model(teslaApi, rfidData)
                            rfidData.save()

                        # Force update
                        chargeState = teslaApi.getChargeStateWithId(id=rfidData.vehicle_id, update=True)

                        if chargeState is not None:
                            self.__logger.debug("monitor() chargeState (not None)")
                            # Send change notification
                            WebSocketUtil.emit(
                                wsEmitQueue=oppleoConfig.wsEmitQueue,
                                event='vehicle_charge_status_update', 
                                id=oppleoConfig.chargerName,
                                data={ 'chargeState': formatChargeState(chargeState),
                                    'vehicle'    : formatVehicle(teslaApi.getVehicleWithId(rfidData.vehicle_id))
                                },
                                namespace='/charge_session',
                                public=True
                                )
                            # len(oppleoConfig.connectedClients) == 0
                        else:
                            self.__logger.debug('monitor() - could not get charge state (None)')

                else: 
                    # len(oppleoConfig.connectedClients) == 0
                    self.__logger.debug('monitor() no connectedClients to report chargeState to. Skip and go directly to sleep.')

            # Sleep for quite a while, and yield for other threads
            time.sleep(self.__sleepInterval)
            monitorInterval = (monitorInterval + self.__sleepInterval)

        self.__logger.info("Stopping VehicleChargeStatusMonitorThread")


    def start(self):
        self.__stop_event.clear()
        self.__logger.debug('Launching Thread...')

        self.__thread = threading.Thread(target=self.monitor, name='VehicleChargeStatusMonitorThread')
        self.__thread.start()

    def stop(self, block=False):
        self.__logger.debug('Requested to stop')
        self.__stop_event.set()
