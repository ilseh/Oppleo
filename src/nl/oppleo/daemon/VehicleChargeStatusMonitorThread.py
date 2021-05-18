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

from nl.oppleo.utils.TokenMediator import tokenMediator

HTTP_CODE_200_OK                    = 200
HTTP_CODE_303_SEE_OTHER             = 303  # Conflict, POST on existing resource
HTTP_CODE_400_BAD_REQUEST           = 400
HTTP_CODE_401_UNAUTHORIZED          = 401
HTTP_CODE_403_FORBIDDEN             = 403
HTTP_CODE_404_NOT_FOUND             = 404
HTTP_CODE_405_METHOD_NOT_ALLOWED    = 405
HTTP_CODE_409_CONFLICT              = 409
HTTP_CODE_410_GONE                  = 410
HTTP_CODE_424_FAILED_DEPENDENCY     = 424
HTTP_CODE_500_INTERNAL_SERVER_ERROR = 500
HTTP_CODE_501_NOT_IMPLEMENTED       = 501

oppleoConfig = OppleoConfig()

class VehicleChargeStatusMonitorThread(object):
    __thread = None
    __threadLock = None
    __logger = None
    __stop_event = None

    __rfidTag = None        # The ID string

    # Check every minute [20 seconds]
    __vehicleMonitorInterval = 20
    __sleepInterval = 0.25
    __requestChargeStatusNow = False
    __requestVehicleWakeupNow = False

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

    @property
    def vehicleMonitorInterval(self):
        return self.__vehicleMonitorInterval


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
            return False

        rfidData = RfidModel.get_one(self.__rfidTag)
        if rfidData is None:
            self.__logger.error('monitor() Cannot run Thread. Cannot get data for RFID {}'.format(self.__rfidTag))

        monitorInterval = (self.__vehicleMonitorInterval + self.__sleepInterval)
        
        while not self.__stop_event.is_set():
            if monitorInterval > self.__vehicleMonitorInterval or self.__requestChargeStatusNow or self.__requestVehicleWakeupNow:
                monitorInterval = 0
                with self.__threadLock:
                    self.__requestChargeStatusNow = False
                self.__logger.debug("monitor() loop")
                if len(oppleoConfig.connectedClients) > 0 and oppleoConfig.vehicleDataOnDashboard:
                    self.__logger.debug("monitor() connected clients ({})".format(len(oppleoConfig.connectedClients)))
                    # See if something changes (could be added or retracted)

                    if rfidData is None or rfidData.api_access_token is None:
                        # No token? Try once more
                        rfidData = RfidModel.get_one(self.__rfidTag)
                        if rfidData is None or rfidData.api_access_token is None:
                            # Still no token, next While iteration
                            self.__logger.debug("monitor() no token, continue to next While iteration")
                            continue

                    # Token, checkout
                    tKey = tokenMediator.checkout(token=rfidData.api_access_token, ref='VehicleStatusMonitorThread: '+rfidData.rfid, wait=True)
                    self.__logger.debug("monitor() tokenMediator.checkout returned key {}".format(tKey))

                    if tKey is None:
                        # Checkout failed? Token must not be valid anymore
                        if not tokenMediator.validate(token=rfidData.api_access_token):
                            self.__logger.debug("monitor() token not valid, continue to next While iteration")
                            # Make sure we reload the RFID tag data next loop
                            rfidData = None
                            with self.__threadLock:
                                self.__requestChargeStatusNow = False
                            continue

                    UpdateOdometerTeslaUtil.copy_token_from_rfid_model_to_api(rfidData, teslaApi)

                    if not teslaApi.hasValidToken():
                        # Not valid, invalidate and continue
                        tokenMediator.invalidate(token=rfidData.api_access_token, key=tKey, ref='VehicleStatusMonitorThread: '+rfidData.rfid,)
                        # Make sure we reload the RFID tag data next loop
                        rfidData = None
                        if self.__requestVehicleWakeupNow:
                            self.clearVehicleWakeupRequest(resultCode=HTTP_CODE_424_FAILED_DEPENDENCY, msg='No valid token')
                        continue

                    self.__logger.debug("monitor() valid token")

                    # Refresh if required
                    if teslaApi.refreshTokenIfRequired():
                        # Invalidate the old token
                        tokenMediator.invalidate(token=rfidData.api_access_token, key=tKey, ref='VehicleStatusMonitorThread: '+rfidData.rfid)
                        UpdateOdometerTeslaUtil.copy_token_from_api_to_rfid_model(teslaApi, rfidData)
                        # Checkout the new token
                        tKey = tokenMediator.checkout(token=rfidData.api_access_token, ref='VehicleStatusMonitorThread: '+rfidData.rfid, wait=True)
                        rfidData.save()

                    self.__logger.debug("monitor() [1] tKey={}".format(tKey))

                    # Force update, for now do not wakeup
                    # TODO - add wakeup as parameter
                    chargeState = teslaApi.getChargeStateWithId(id=rfidData.vehicle_id, 
                                                                update=True, 
                                                                wakeUpWhenSleeping=False or self.__requestVehicleWakeupNow
                                                               )

                    if self.__requestVehicleWakeupNow:
                        self.clearVehicleWakeupRequest(resultCode=HTTP_CODE_200_OK if chargeState is not None else HTTP_CODE_424_FAILED_DEPENDENCY,
                                                       msg='Vehicle awake' if chargeState is not None else 'Could not wakeup vehicle'
                                                      )

                    self.__logger.debug("monitor() [2] tKey={}".format(tKey))

                    # Release the token
                    tokenMediator.release(token=rfidData.api_access_token, key=tKey)

                    if chargeState is not None and oppleoConfig.vehicleDataOnDashboard:
                        self.__logger.debug("monitor() chargeState (not None)")
                        # Send change notification
                        WebSocketUtil.emit(
                            wsEmitQueue     = oppleoConfig.wsEmitQueue,
                            event           = 'vehicle_charge_status_update', 
                            id              = oppleoConfig.chargerName,
                            data            = { 'chargeState'            : formatChargeState(chargeState),
                                                'vehicle'                : formatVehicle(teslaApi.getVehicleWithId(rfidData.vehicle_id)),
                                                'vehicleMonitorInterval' : self.__vehicleMonitorInterval
                            },
                            namespace       = '/charge_session',
                            public          = False
                            )
                        # len(oppleoConfig.connectedClients) == 0
                    else:
                        self.__logger.debug('monitor() - could not get charge state (None)')
                        if teslaApi.vehicleWithIdIsAsleep(id=rfidData.vehicle_id):
                            # Send change notification - vehicle asleep
                            WebSocketUtil.emit(
                                wsEmitQueue = oppleoConfig.wsEmitQueue,
                                event       = 'vehicle_charge_status_update', 
                                id          = oppleoConfig.chargerName,
                                data        = { 'chargeState'            : formatChargeState(chargeState),
                                                                           # No need to update vehicle information, done when requesting charge state
                                                'vehicle'                : formatVehicle(teslaApi.getVehicleWithId(id=rfidData.vehicle_id, update=False)),
                                                'vehicleMonitorInterval' : self.__vehicleMonitorInterval
                                },
                                namespace   = '/charge_session',
                                public      = False
                                )
                else: 
                    # len(oppleoConfig.connectedClients) == 0
                    self.__logger.debug('monitor() no connectedClients to report chargeState to or display not enabled. Skip and go directly to sleep.')

                    self.clearVehicleWakeupRequest(resultCode=HTTP_CODE_410_GONE,
                                                   msg='No clients connected'
                                                  )

            # Sleep for quite a while, and yield for other threads
            time.sleep(self.__sleepInterval)
            monitorInterval = (monitorInterval + self.__sleepInterval)

        self.__logger.info("Stopping VehicleChargeStatusMonitorThread")


    """
        Causes the monitor loop to timeout now
    """ 
    def requestChargeStatusUpdate(self):
        with self.__threadLock:
            self.__requestChargeStatusNow = True

    """
        Causes the monitor loop to timeout now and wake up the vehicle
    """ 
    def requestVehicleWakeup(self):
        with self.__threadLock:
            self.__requestVehicleWakeupNow = True

    def clearVehicleWakeupRequest(self, resultCode:int=500, msg:str='Unknown'):
        with self.__threadLock:
            self.__requestVehicleWakeupNow = False

        # Send wakeup result notification
        WebSocketUtil.emit(
            wsEmitQueue = oppleoConfig.wsEmitQueue,
            event       = 'vehicle_status_update', 
            id          = oppleoConfig.chargerName,
            data        = { 'request' : 'wakeupVehicle',
                            'result'  : resultCode,
                            'msg'     : msg
            },
            namespace   = '/charge_session',
            public      = False
            )

    def start(self):
        self.__stop_event.clear()
        self.__logger.debug('Launching Thread...')

        self.__thread = threading.Thread(target=self.monitor, name='VehicleChargeStatusMonitorThread')
        self.__thread.start()

    def stop(self, block=False):
        self.__logger.debug('Requested to stop')
        self.__stop_event.set()
