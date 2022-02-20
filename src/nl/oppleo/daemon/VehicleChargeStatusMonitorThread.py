import threading
import logging
import time
import re

from nl.oppleo.config.OppleoConfig import OppleoConfig
from nl.oppleo.utils.OutboundEvent import OutboundEvent
from nl.oppleo.api.VehicleApi import VehicleApi
from nl.oppleo.models.RfidModel import RfidModel

#from nl.oppleo.utils.TokenMediator import tokenMediator

HTTP_CODE_200_OK                    = 200
HTTP_CODE_202_ACCEPTED              = 202  # Accepted, processing pending
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
        - Creates VehicleApi 
        - If the number of Online clients present in list(oppleoConfig.connectedClients) 
            - Get charge state
        - Interval 60 sec (ophalen info kost ~10 sec met TeslaAPI)
        When the session is stopped this Thread is destroyed. With a new session a new Thread is started.
    """
    def monitor(self):
        global oppleoConfig
        
        self.__logger.debug('monitor()')


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

                    if rfidData is None:
                        # No token? Try once more
                        rfidData = RfidModel.get_one(self.__rfidTag)
                        if rfidData is None:
                            # Still no token, next While iteration
                            self.__logger.debug("monitor() no token, continue to next While iteration")
                            continue

                    vApi = VehicleApi(rfid_model=rfidData)
                    if not vApi.isAuthorized():
                        # no token, next While iteration
                        self.__logger.debug("monitor() VehicleApi not authorized, continue to next While iteration")
                        continue

                    # Force update, for now do not wakeup
                    chargeState = vApi.getChargeState(wake_up=oppleoConfig.wakeupVehicleOnDataRequest or 
                                                              self.__requestVehicleWakeupNow
                                                     )
                    if self.__requestVehicleWakeupNow:
                        self.clearVehicleWakeupRequest(resultCode=HTTP_CODE_200_OK if chargeState is not None else HTTP_CODE_424_FAILED_DEPENDENCY,
                                                       msg='Vehicle awake' if chargeState is not None else 'Could not wakeup vehicle'
                                                      )

                    # Did the token still work?
                    if chargeState is None:
                        # Nah, report
                        self.__logger.warn('Could not obtain charge state.')
                        # Skip to next cycle
                        continue
                    self.__logger.debug("monitor() chargeState (not None)")

                    if oppleoConfig.vehicleDataOnDashboard:
                        # Send change notification
                        OutboundEvent.triggerEvent(
                            event           = 'vehicle_charge_status_update', 
                            id              = oppleoConfig.chargerName,
                            data            = { 'chargeState'            : chargeState,
                                                'vehicle'                : vApi.getVehicle(),
                                                'vehicleMonitorInterval' : self.__vehicleMonitorInterval
                            },
                            namespace       = '/charge_session',
                            public          = False
                            )
                        # len(oppleoConfig.connectedClients) == 0
                    """
                        TODO: verify if ok when vehicle is asleep?
                    """

                else: 
                    # len(oppleoConfig.connectedClients) == 0
                    self.__logger.debug('monitor() no connectedClients to report chargeState to or vehicle status display not enabled. Skip and go directly to sleep.')

                    # Not sending any notifications when no clients are connected or vehicle monitoring on dashboard is switched off

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

        # Send wakeup request notification
        OutboundEvent.triggerEvent(
            event       = 'vehicle_status_update', 
            id          = oppleoConfig.chargerName,
            data        = { 'request' : 'wakeupVehicle',
                            'result'  : HTTP_CODE_202_ACCEPTED,
                            'msg'     : 'Waking up vehicle'
            },
            namespace   = '/charge_session',
            public      = False
            )

    def clearVehicleWakeupRequest(self, resultCode:int=500, msg:str='Unknown'):
        with self.__threadLock:
            self.__requestVehicleWakeupNow = False

        # Send wakeup result notification
        OutboundEvent.triggerEvent(
            event       = 'vehicle_status_update', 
            id          = oppleoConfig.chargerName,
            data        = { 'request' : 'clearWakeupVehicle',
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
