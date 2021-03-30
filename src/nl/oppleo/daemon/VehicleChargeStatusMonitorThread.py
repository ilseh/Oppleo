import threading
import logging
import time
import re

from nl.oppleo.config.OppleoConfig import OppleoConfig
from nl.oppleo.utils.WebSocketUtil import WebSocketUtil
from nl.oppleo.api.TeslaApi import TeslaAPI
from nl.oppleo.utils.UpdateOdometerTeslaUtil import UpdateOdometerTeslaUtil
from nl.oppleo.utils.FormatChargeState import formatChargeState


oppleoConfig = OppleoConfig()

class VehicleChargeStatusMonitorThread(object):
    thread = None
    threadLock = None
    logger = None
    stop_event = None

    rfidTag = None

    # Check every minute [60 seconds]
    vehicleMonitorInterval = 60

    sleepInterval = 0.25

    def __init__(self):
        self.threadLock = threading.Lock()
        self.stop_event = threading.Event()
        self.logger = logging.getLogger('nl.oppleo.daemon.VehicleChargeStatusMonitorThread')


    @property
    def rfid(self, rfidValue = None):
        if self.thread is not None:
            if self.thread.is_alive():
                self.logger.error('Cannot set RFID after Thread is started!')
            else:
                self.logger.error('Cannot set RFID after Thread is finished!')
            return
        if rfidValue is None:
            self.logger.error('Cannot set RFID to None!')
        self.rfidTag = rfidValue





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
        self.logger.debug('monitor()')

        teslaApi = TeslaAPI()

        if self.rfidTag is None:
            self.logger.error('monitor() Cannot run Thread for RFID None!')

        while not self.stop_event.is_set():
            if len(oppleoConfig.connectedClients) > 0:
                # See if something changes (could be added or retracted)
                UpdateOdometerTeslaUtil.copy_token_from_rfid_model_to_api(self.rfidTag, teslaApi)

                if teslaApi.hasValidToken():
                    # Refresh if required (check once per day)
                    if teslaApi.refreshTokenIfRequired():
                        UpdateOdometerTeslaUtil.copy_token_from_api_to_rfid_model(teslaApi, self.rfidTag)
                        self.rfidTag.save()

                    chargeState = teslaApi.getChargeStateWithId(self.rfidTag.vehicle_id)

                    if chargeState is not None:
                        # Send change notification
                        WebSocketUtil.emit(
                            wsEmitQueue=oppleoConfig.wsEmitQueue,
                            event='vehicle_charge_status_update', 
                            id=oppleoConfig.chargerName,
                            data=formatChargeState(chargeState),
                            namespace='/charge_session',
                            public=True
                            )
                        # len(oppleoConfig.connectedClients) == 0
                    else:
                        self.logger.debug('monitor() - could not get charge state (None)')

            else: 
                # len(oppleoConfig.connectedClients) == 0
                self.logger.debug('monitor() no connectedClients to report chargeState to. Skip and go directly to sleep.')

            # Sleep for quite a while, and yield for other threads
            time.sleep(self.sleepInterval)

        self.logger.info("Stopping VehicleChargeStatusMonitorThread")


    def start(self):
        self.stop_event.clear()
        self.logger.debug('Launching Thread...')

        self.thread = threading.Thread(target=self.monitor, name='VehicleChargeStatusMonitorThread')
        self.thread.start()

    def stop(self, block=False):
        self.logger.debug('Requested to stop')
        self.stop_event.set()
