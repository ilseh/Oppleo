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
from nl.oppleo.services.led.RGBLedControllerThread import RGBLedControllerThread
from nl.oppleo.daemon.VehicleChargeStatusMonitorThread import VehicleChargeStatusMonitorThread
from nl.oppleo.models.ChargeSessionModel import ChargeSessionModel
from nl.oppleo.models.ChargerConfigModel import ChargerConfigModel
from nl.oppleo.models.EnergyDeviceMeasureModel import EnergyDeviceMeasureModel
from nl.oppleo.models.RfidModel import RfidModel
from nl.oppleo.services.Buzzer import Buzzer
from nl.oppleo.services.Evse import Evse
from nl.oppleo.services.EvseReader import EvseReader
from nl.oppleo.services.EvseReaderProd import EvseState
from nl.oppleo.services.RfidReader import RfidReader
from nl.oppleo.utils.ModulePresence import ModulePresence
from nl.oppleo.utils.UpdateOdometerTeslaUtil import UpdateOdometerTeslaUtil
from nl.oppleo.utils.OutboundEvent import OutboundEvent 


oppleoSystemConfig = OppleoSystemConfig()
oppleoConfig = OppleoConfig()

 
class ChargerHandlerThread(object):
    threadLock = None
    appSocketIO = None
    logger = None
    evse_reader_thread = None
    rfid_reader_thread = None
    stop_event = None
    charger = None
    buzzer = None
    evse = None
    evse_reader = None
    is_status_charging = False
    device = None
    counter = 0
    __rfidreader = None

    def __init__(self, device, buzzer, evse, evse_reader, appSocketIO):
        self.threadLock = threading.Lock()
        self.logger = logging.getLogger('nl.oppleo.daemon.ChargerHandlerThread')
        self.evse_reader_thread = None
        self.rfid_reader_thread = None
        self.stop_event = threading.Event()
        self.buzzer = buzzer
        self.evse = evse
        self.evse_reader = evse_reader
        self.is_status_charging = False
        self.appSocketIO = appSocketIO
        self.device = device


    def start(self):
        self.stop_event.clear()
        self.logger.debug('Launching Threads...')

        self.logger.debug('.start() - start RGBLedControllerThread')
        oppleoConfig.rgblcThread = RGBLedControllerThread()
        oppleoConfig.rgblcThread.start()

        self.logger.debug('.start() - start_background_task - evseReaderLoop')
        # self.evse_reader_thread = self.appSocketIO.start_background_task(self.evse_reader_thread)
        #   appSocketIO.start_background_task launches a background_task
        #   This really doesn't do parallelism well, basically runs the whole thread befor it yields...
        #   Therefore use standard threads
        self.evse_reader_thread = threading.Thread(target=self.evseReaderLoop, name='EvseLedReaderThread')
        self.evse_reader_thread.start()

        self.logger.debug('.start() start_background_task - rfidReaderLoop')
        # self.rfid_reader_thread = self.appSocketIO.start_background_task(self.rfidReaderLoop)
        #   appSocketIO.start_background_task launches a background_task
        #   This really doesn't do parallelism well, basically runs the whole thread befor it yields...
        #   Therefore use standard threads
        self.__rfidReader = RfidReader()
        self.rfid_reader_thread = threading.Thread(target=self.rfidReaderLoop, name='RfidReaderThread')
        self.rfid_reader_thread.start()

        self.logger.debug('.start() - Done starting rfid reader and evse reader background tasks')


    # evse_reader_thread
    def evseReaderLoop(self):
        global oppleoConfig

        try:
            self.evse_reader.loop(self.stop_event.is_set, lambda evse_state: self.try_handle_charging(evse_state))
        except Exception as e:
            self.logger.exception('.evseReaderLoop() - Could not start evse reader loop {}'.format(str(e)))
            oppleoConfig.rgblcThread.error = True


    # rfid_reader_thread
    def isExpired(self, from_date, until_date):
        expired = False
        if from_date:
            expired = datetime.now() < from_date
        if not expired and until_date:
            expired = datetime.now() > until_date
        return expired

    # webapp thread
    # rfid_reader_thread
    def rfidAuthorized(self, rfid:str) -> bool:
        self.logger.debug(".rfidAuthorized() - rfid:{}".format(rfid))

        rfidData = RfidModel.get_one(rfid)
        if rfidData is None:
            self.logger.warn("Unknown rfid offered ({}). Access denied and rfid value saved in db.".format(rfid))
            newRfid = RfidModel()
            newRfid.set({"rfid": rfid})
            newRfid.save()
            return False

        # Update last seen date
        rfidData.last_used_at = datetime.now()
        rfidData.save()

        # Valid rfid card?
        return rfidData.enabled and not self.isExpired(rfidData.valid_from, rfidData.valid_until)


    # rfid_reader_thread
    def resume_session_if_applicable(self):
        self.logger.debug(".resume_session_if_applicable()")

        # Check if there was a charge session active when Oppleo was stopped.
        openChargeSession = ChargeSessionModel.getOpenChargeSession(self.device)
        if openChargeSession is None:
            self.logger.info("No open charge session to resume.")
        else:
            self.logger.info("Resume charge session {} for rfid {}".format(openChargeSession.id, openChargeSession.rfid))
            # Start the VehicleChargeStatusMonitorThread
            oppleoConfig.vcsmThread = VehicleChargeStatusMonitorThread()
            oppleoConfig.vcsmThread.rfid = openChargeSession.rfid
            oppleoConfig.vcsmThread.start()
        self.update_charger_and_led(openChargeSession is not None)


    # rfid_reader_thread
    def rfidReaderLoop(self):
        self.resume_session_if_applicable()
        while not self.stop_event.is_set():

            if oppleoSystemConfig.rfidEnabled:
                # Returns [int, str]
                rfid, text = self.__rfidReader.read()
                self.logger.info("Handle rfid:{} text:{}".format(rfid, text))
                self.handleOfferedRfid(str(rfid))

            # Sleep to prevent re-reading the same tag twice
            # time.sleep(0.25)
            time.sleep(0.75)

        self.logger.info(".rfidReaderLoop() - Stopping RfidReader")

    def rfidReaderLog(self):
        if self.__rfidReader is not None:
            return self.__rfidReader.read_log()
        return {}

    # rfid_reader_thread
    def is_other_session_active(self, last_saved_session, rfid):
        return last_saved_session and not last_saved_session.end_value \
               and last_saved_session.rfid != str(rfid)


    # rfid_reader_thread
    def handleOfferedRfid(self, rfid:str):
        self.logger.debug(".handleOfferedRfid() - rfid {}".format(rfid))
        """
        TODO - hand callback function to check off-peak from the thread
        """

        # An RFID tag was read, lock to prevent thread mixing
        with self.threadLock:

            """
                Case 1: open session. only the rfid used for this session can deactivate it.
                Case 2: no open session. only a valid rfid can open the session
            """
            openSession = ChargeSessionModel.getOpenChargeSession(self.device)

            if openSession is not None:
                # Case 1
                if openSession.rfid != rfid:
                    # No go (Case 1)
                    self.logger.info("Rfid [id={}][type={}] cannot stop charge session started by rfid [id={}][type={}]".format(
                        rfid, type(rfid), openSession.rfid, type(openSession.rfid)))
                    self.buzz_error()
                    oppleoConfig.rgblcThread.errorFlash = True
                    return
                else:
                    # Correct rfid, close session (Case 1)
                    self.logger.info("Rfid [id={}][type={}] stop charge session started by rfid [id={}][type={}]".format(
                        rfid, type(rfid), openSession.rfid, type(openSession.rfid)))
#                    self.logger.info("Rfid {} stop charge session".format(rfid))
                    self.buzz_ok()
                    # Set end-time to now (when RFID was presented)
                    self.end_charge_session(charge_session=openSession, detect=False)
                    self.update_charger_and_led(False)
                    return
            else:
                # Case 2
                if self.rfidAuthorized(rfid):
                    # Valid rfid, open charge session (Case 2)
                    self.logger.info("Starting new charging session for rfid {}".format(rfid))
                    self.buzz_ok()
                    # Do not condense, an actual RFID was presented
                    self.start_charge_session(
                            rfid=rfid,
                            trigger=ChargeSessionModel.TRIGGER_RFID,
                            condense=False
                            )
                    self.update_charger_and_led(True)
                    return
                else:
                    # Invalid rfid, no new charge session (Case 2)
                    self.buzz_error()
                    oppleoConfig.rgblcThread.errorFlash = True
                    return


    # evse_reader_thread
    # rfid_reader_thread
    # main thread (though web)
    def start_charge_session(self, rfid:str, trigger=ChargeSessionModel.TRIGGER_RFID, condense=False):
        global oppleoConfig

        self.logger.debug(".start_charge_session() new charging session for rfid {}".format(rfid))

        # Optimize: maybe get this from the latest db value rather than from the energy meter directly

        start_value = 0
        if (oppleoConfig.energyDevice is not None and 
            oppleoConfig.energyDevice.enabled and
            oppleoConfig.energyDevice.energyModbusReader is not None):
            start_value = oppleoConfig.energyDevice.energyModbusReader.getTotalKWHHValue()
            self.logger.debug(".start_charge_session() start_value from energyModbusReader: {}".format(start_value))

        data_for_session = {
            "rfid"              : rfid, 
            "energy_device_id"  : self.device,
            "start_value"       : start_value,
            "tariff"            : ChargerConfigModel.get_config().charger_tariff,
            "end_value"         : start_value,
            "total_energy"      : 0,
            "total_price"       : 0,
            "trigger"           : trigger
            }
        charge_session = ChargeSessionModel()
        charge_session.set(data_for_session)
        charge_session.save()
        self.logger.info('.start_charge_session() New charge session started with {}'.format(charge_session.id))

        rfidObj = RfidModel.get_one(rfid)
        if rfidObj.vehicle_make.upper() == "TESLA" and rfidObj.get_odometer: 
            # Try to add odometer
            self.logger.debug('.start_charge_session() Update odometer for this Tesla')
            self.save_tesla_values_in_thread(
                    charge_session_id=charge_session.id,
                    condense=condense
                    )
        # Emit websocket update
        self.logger.debug('.start_charge_session() Send msg charge_session_started event ...{}'.format(charge_session.to_str))
        OutboundEvent.triggerEvent(
                    event='charge_session_started', 
                    id=oppleoConfig.chargerName,
                    data=charge_session.to_str(),
                    namespace='/charge_session',
                    public=False
                )
        # Start the VehicleChargeStatusMonitorThread
        oppleoConfig.vcsmThread = VehicleChargeStatusMonitorThread()
        oppleoConfig.vcsmThread.rfid = rfid
        oppleoConfig.vcsmThread.start()



    # evse_reader_thread
    # rfid_reader_thread
    # lock threads before calling this
    def end_charge_session(self, charge_session, detect=False):
        global oppleoConfig

        charge_session.end_value = 0

        start_value = 0
        if (oppleoConfig.energyDevice is not None and 
            oppleoConfig.energyDevice.enabled and
            oppleoConfig.energyDevice.energyModbusReader is not None):
            charge_session.end_value = oppleoConfig.energyDevice.energyModbusReader.getTotalKWHHValue()
            self.logger.debug(".end_charge_session() - end_value from energyModbusReader: {}".format(charge_session.end_value))

        if detect:
            # end_time is the time the kWh was updated to this value, and the current went to 0
            end_time = EnergyDeviceMeasureModel.get_time_of_kwh(
                            charge_session.energy_device_id,
                            charge_session.end_value
                            )
            charge_session.end_time = end_time if end_time is not None else datetime.now()
            self.logger.debug('.end_charge_session() - Detected end time is {}'.format(charge_session.end_time.strftime("%d/%m/%Y, %H:%M:%S")))
        else:
            charge_session.end_time = datetime.now()
        charge_session.total_energy = charge_session.end_value - charge_session.start_value
        charge_session.total_price = round(charge_session.total_energy * charge_session.tariff * 100) /100
        charge_session.save()
        # Emit websocket update
        self.logger.debug('.end_charge_session() - Send msg charge_session_ended ...'.format(charge_session.to_str))
        OutboundEvent.triggerEvent(
                event='charge_session_ended', 
                id=oppleoConfig.chargerName,
                data=charge_session.to_str(),
                namespace='/charge_session',
                public=False
            )
        # Stop the VehicleChargeStatusMonitorThread
        if oppleoConfig.vcsmThread is not None:
            oppleoConfig.vcsmThread.stop()
            oppleoConfig.vcsmThread = None
            


    # evse_reader_thread
    # rfid_reader_thread
    # charge_session_id is the row id in the database table
    def save_tesla_values_in_thread(self, charge_session_id, condense=False):
        self.logger.debug('.save_tesla_values_in_thread() id = {} and condense = {}'.format(charge_session_id, condense))
        uotu = UpdateOdometerTeslaUtil()
        uotu.charge_session_id = charge_session_id
        uotu.condense = condense
        # update_odometer takes some time, so put in own thread

        # uotu.start()
        # start() launches a background_task by calling socketio.start_background_task
        #   This really doesn't do parallelism well, basically runs the whole thread befor it yields...
        #   Therefore use standard threads
        if oppleoConfig.vuThread is not None and oppleoConfig.vuThread.is_alive():
            self.logger.warning('.save_tesla_values_in_thread() VehicleUpdateThread was running (odometer) - running another one')
        oppleoConfig.vuThread = threading.Thread(target=uotu.update_odometer, name='TeslaUtilThread')
        oppleoConfig.vuThread.start()


    # rfid_reader_thread
    def update_charger_and_led(self, start_session):
        if start_session:
            self.evse.switch_on()
        else:
            self.evse.switch_off()
        oppleoConfig.rgblcThread.openSession = start_session


    def stop(self, block=False):
        self.logger.debug('.stop() - Requested to stop')
        if oppleoConfig.rgblcThread is not None:
            oppleoConfig.rgblcThread.stop()
        self.stop_event.set()


    # evse_reader_thread
    def try_handle_charging(self, evse_state):
        try:
            self.handle_charging(evse_state)
        except Exception as e:
            self.logger.error(".try_handle_charging() - Error handle charging: %s", e, exc_info=True)
            oppleoConfig.rgblcThread.error = True



    # evse_reader_thread
    def handle_charging(self, evse_state):
        if evse_state == EvseState.EVSE_STATE_CHARGING:
            # self.logger.debug("Device is currently charging")
            if not self.is_status_charging:
                # Switching to charging
                """
                 AUTO CHARGE SESSION
                  Automatic detect new charge sessions. When the car is present, it keeps using limited amounts of
                  energy. (Tesla Model 3 0.2kWh each 1:23h). If this usage has not occurred, and now the EVSE
                  goes to charging again, the car probably has gone away and returned.
                """
                self.handle_auto_session()

                self.is_status_charging = True
                self.logger.debug('.handle_charging() - Send msg charge_session_status_update ...{}'.format(evse_state))
                OutboundEvent.triggerEvent(
                        event='charge_session_status_update', 
                        status=evse_state, 
                        id=oppleoConfig.chargerName, 
                        namespace='/charge_session',
                        public=True
                    )
            self.logger.debug('.handle_charging() - Start charging light pulse')
            oppleoConfig.rgblcThread.charging = True

        else:
            # self.logger.debug("Not charging")
            # Not charging. If it was charging, set light back to previous (before charging) light
            if self.is_status_charging:
                self.is_status_charging = False
                self.logger.debug(".handle_charging() - Charging is stopped")
                self.logger.debug('.handle_charging() - Send msg charge_session_status_update ...'.format(evse_state))
                OutboundEvent.triggerEvent(
                        event='charge_session_status_update', 
                        # INACTIVE IS ALSO CONNECTED
                        status=EvseState.EVSE_STATE_CONNECTED, 
                        id=oppleoConfig.chargerName, 
                        namespace='/charge_session',
                        public=True
                    )

        if oppleoConfig.rgblcThread.charging != (evse_state == EvseState.EVSE_STATE_CHARGING):
            # Only the change
            self.logger.debug('.handle_charging() - Charging light pulse to {}'.format(str(evse_state == EvseState.EVSE_STATE_CHARGING)))
            oppleoConfig.rgblcThread.charging = (evse_state == EvseState.EVSE_STATE_CHARGING)



    # Auto Session starts a new session when the EVSE starts charging and during the set amount of minutes less
    # than the amount of energy has been consumed (auto was away)
    # A Tesla Model 3 75kWh Dual Motor charges 0.2kWh every 1:23h (16 feb 2020)
    # Only called upon switch from not-charging to charging by the EVSE, so a session is ongoin
    # evse_reader_thread
    def handle_auto_session(self):
        self.logger.debug('.handle_auto_session() enabled: {}'.format(oppleoConfig.autoSessionEnabled))
        # Open session, otherwise this method is not called
        if oppleoConfig.autoSessionEnabled: 
            edmm = EnergyDeviceMeasureModel()
            kwh_used = edmm.get_usage_since(
                    oppleoConfig.chargerName,
                    (datetime.today() - timedelta(minutes=oppleoConfig.autoSessionMinutes))
                    )
            if kwh_used > oppleoConfig.autoSessionEnergy:
                self.logger.debug('.handle_auto_session() - Keep the current session. More energy ({}kWh) used than {}kWh in {} minutes'
                           .format(
                                kwh_used,
                                oppleoConfig.autoSessionEnergy, 
                                oppleoConfig.autoSessionMinutes
                            )
                        )
            else:
                self.logger.info('.handle_auto_session() - Start a new session (auto-session). Less energy ({}kWh) used than {}kWh in {} minutes'
                           .format(
                                kwh_used,
                                oppleoConfig.autoSessionEnergy,
                                oppleoConfig.autoSessionMinutes
                            )
                        )
                with self.threadLock:
                    # Lock to prevent the session to be hijacked when someone simultaneously presents the rfid card
                    charge_session = ChargeSessionModel.get_open_charge_session_for_device(self.device)
                    # Try to detect the last power consumption
                    self.end_charge_session(charge_session, True)
                    # Verify if the auto session was generated correctly. If the odometer value is equal, the session should be condensed
                    # Condense after the odometer update has completed! Done in the same thread
                    self.start_charge_session(
                            rfid=charge_session.rfid,
                            trigger=ChargeSessionModel.TRIGGER_AUTO,
                            condense=oppleoConfig.autoSessionCondenseSameOdometer
                            )


    # rfid_reader_thread
    def buzz_ok(self):
        self.buzzer.buzz_other_thread(.1, 1)

    # rfid_reader_thread
    def buzz_error(self):
        self.buzzer.buzz_other_thread(.1, 2)

    # Callback from MeasureElectricityUsageThread with updated EnergyDeviceMeasureModel
    def energyUpdate(self, device_measurement):
        self.logger.debug('.energyUpdate() callback...')
        # Open charge session for this energy device?
        with self.threadLock:
            open_charge_session_for_device = \
                ChargeSessionModel.get_open_charge_session_for_device(
                        device_measurement.energy_device_id
                )
            if open_charge_session_for_device != None:
                self.logger.debug('.energyUpdate() open charge session, updating usage. device_measurement {}, open_charge_session_for_device {}'.format(str(device_measurement.to_str()), str(open_charge_session_for_device.to_str())))
                # Update session usage
                open_charge_session_for_device.end_value = device_measurement.kw_total
                self.logger.debug('.energyUpdate() end_value to %s...' % open_charge_session_for_device.end_value)
                open_charge_session_for_device.total_energy = \
                    round((open_charge_session_for_device.end_value - open_charge_session_for_device.start_value) *10) /10
                self.logger.debug('.energyUpdate() total_energy to %s...' % open_charge_session_for_device.total_energy)
                open_charge_session_for_device.total_price = \
                    round(open_charge_session_for_device.total_energy * open_charge_session_for_device.tariff * 100) /100 
                self.logger.debug('.energyUpdate() total_price to %s...' % open_charge_session_for_device.total_price)
                open_charge_session_for_device.save() 
                # Emit change events

                self.counter += 1
                self.logger.debug('.energyUpdate() Send msg {} for charge_session_data_update ...'.format(self.counter))
                # Emit only to authenticated users, not public
                OutboundEvent.triggerEvent(
                        event='charge_session_data_update', 
                        id=oppleoConfig.chargerName,
                        data=open_charge_session_for_device.to_str(), 
                        namespace='/charge_session',
                        public=False
                    )

