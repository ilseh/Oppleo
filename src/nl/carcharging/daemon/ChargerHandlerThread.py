import sys
import threading
import time
import logging
from datetime import datetime, timedelta

from injector import inject
from service import Service

from nl.carcharging.config.WebAppConfig import WebAppConfig
from nl.carcharging.models.ChargeSessionModel import ChargeSessionModel
from nl.carcharging.models.ChargerConfigModel import ChargerConfigModel
from nl.carcharging.models.EnergyDeviceMeasureModel import EnergyDeviceMeasureModel
from nl.carcharging.models.RfidModel import RfidModel
from nl.carcharging.services.Buzzer import Buzzer
from nl.carcharging.services.Charger import Charger
from nl.carcharging.services.Evse import Evse
from nl.carcharging.services.EvseReader import EvseReader
from nl.carcharging.services.EvseReaderProd import EvseState
from nl.carcharging.services.LedLighter import LedLighter
from nl.carcharging.services.RfidReader import RfidReader
from nl.carcharging.utils.EnergyUtil import EnergyUtil
from nl.carcharging.utils.GenericUtil import GenericUtil
from nl.carcharging.utils.UpdateOdometerTeslaUtil import UpdateOdometerTeslaUtil

GenericUtil.importGpio()
GenericUtil.importMfrc522()


SECONDS_IN_HOUR = 60 * 60


class NotAuthorizedException(Exception):
    pass


class OtherRfidHasOpenSessionException(Exception):
    pass


class ExpiredException(Exception):
    pass


class ChargerHandlerThread(object):
    threadLock = None
    appSocketIO = None
    logger = None
    evse_reader_thread = None
    rfid_reader_thread = None
    stop_event = None
    energy_util = None
    charger = None
    ledlighter = None
    buzzer = None
    evse = None
    evse_reader = None
    is_status_charging = False
    device = None
    counter = 0

    def __init__(self, 
                device: device,
                energy_util: EnergyUtil, 
                charger: Charger, 
                ledlighter: LedLighter, 
                buzzer: Buzzer, 
                evse: Evse,
                evse_reader: EvseReader, 
                appSocketIO: appSocketIO
                ):
        self.threadLock = threading.Lock()
        self.logger = logging.getLogger('nl.carcharging.daemon.ChargerHandlerThread')
        self.logger.setLevel(logging.DEBUG)
        self.evse_reader_thread = None
        self.rfid_reader_thread = None
        self.stop_event = threading.Event()
        self.energy_util = energy_util
        self.charger = charger
        self.ledlighter = ledlighter
        self.buzzer = buzzer
        self.evse = evse
        self.evse_reader = evse_reader
        self.is_status_charging = False
        self.appSocketIO = appSocketIO
        self.device = device


    def start(self):
        self.stop_event.clear()
        self.logger.debug('Launching background task...')
        self.logger.debug('start_background_task() - evseReaderLoop')
        self.evse_reader_thread = self.appSocketIO.start_background_task(self.evseReaderLoop)
        self.logger.debug('start_background_task() - rfidReaderLoop')
        self.rfid_reader_thread = self.appSocketIO.start_background_task(self.rfidReaderLoop)
        self.logger.debug('Done starting rfid reader and evse reader backgroubd tasks')


    # evse_reader_thread
    def evseReaderLoop(self):
        # Redirect stdout to logfile
        try:
            # Assume first logger handler is the correct file to route stdout to.
#            sys.stdout = open(self.logger.handlers[0].baseFilename, 'a')
            sys.stdout = open('/tmp/stdout.log', 'a')
#            sys.stdout = open('/home/pi/stdout.log', 'a')

            self.evse_reader.loop(self.stop_event.is_set, lambda evse_state: self.try_handle_charging(evse_state))

        except Exception as e:
            self.logger.exception('Could not start evse reader loop')
            self.ledlighter.error()
        finally:
            print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> flushing stdout', flush=True)


    # rfid_reader_thread
    def authorize(self, rfid):

        is_authorized = False
        is_expired = False
        rfid_data = {}
        try:
            rfid_data = RfidModel.get_one(rfid)
            if rfid_data is None:
                self.logger.warn("Unknown rfid offered. Access denied and rfid value saved in db.")
                new_rfid_entry = RfidModel()
                new_rfid_entry.set({"rfid": rfid})
                new_rfid_entry.save()
            else:
                is_authorized = rfid_data.enabled
                is_expired = self.is_expired(rfid_data.valid_from, rfid_data.valid_until)
                rfid_data.last_used_at = datetime.now()
                rfid_data.save()
        except Exception as e:
            self.logger.error("Could not authorize %s %s" % (rfid, e))

        if not is_authorized:
            raise NotAuthorizedException("Unauthorized rfid %s" % rfid)
        if is_expired:
            raise ExpiredException("Rfid isn't valid yet/anymore. Valid from %s to %s" %
                                   (rfid_data.valid_from, rfid_data.valid_until))


    # rfid_reader_thread
    def is_expired(self, from_date, until_date):
        expired = False
        if from_date:
            expired = datetime.now() < from_date
        if not expired and until_date:
            expired = datetime.now() > until_date
        return expired


    # rfid_reader_thread
    def resume_session_if_applicable(self):
        # Check if there was a session active when this daemon was stopped.
        last_saved_session = ChargeSessionModel.get_latest_charge_session(self.device)

        if last_saved_session and last_saved_session.end_time is None:
            self.logger.info("After startup continuing an active session for rfid %s" % last_saved_session.rfid)
            resume_session = True
        else:
            resume_session = False
        self.update_charger_and_led(resume_session)


    # rfid_reader_thread
    def rfidReaderLoop(self):
        self.resume_session_if_applicable()
        reader = RfidReader()
        while not self.stop_event.is_set():
            try:
                self.read_rfid(reader)
            except Exception as e:
                self.logger.error("Could not execute run_read_rfid: %s" % e)
                self.buzz_error()
                self.ledlighter.error(duration=.6)
            time.sleep(0.25)
        self.logger.info("Stopping RfidReader")


    # rfid_reader_thread
    def is_other_session_active(self, last_saved_session, rfid):
        return last_saved_session and not last_saved_session.end_value \
               and last_saved_session.rfid != str(rfid)


    # rfid_reader_thread
    def read_rfid(self, reader):
        self.logger.info("Starting rfid reader for device %s" % self.device)
        """
        TODO - hand callback function to check off-peak from the thread
        """
        rfid, text = reader.read()
        self.logger.debug("Rfid id and text: %d - %s" % (rfid, text))

        # An RFID tag was read, lock to prevent thread mixing
        with self.threadLock:
            rfid_latest_session = ChargeSessionModel.get_latest_charge_session(self.device, rfid)

            start_session = False
            # If rfid has open session, no need to authorize, let it end the session.
            # If no open session, authorize rfid.
            if self.has_rfid_open_session(rfid_latest_session):
                self.buzz_ok()
                self.logger.debug("Stopping charging session for rfid %s" % rfid)
                self.end_charge_session(rfid_latest_session)
            else:
                self.authorize(rfid)
                self.buzz_ok()

                # If there is an open session for another rfid, raise error.
                last_saved_session = ChargeSessionModel.get_latest_charge_session(self.device)
                if self.is_other_session_active(last_saved_session, rfid):
                    raise OtherRfidHasOpenSessionException(
                        "Rfid %s was offered but rfid %s has an open session" % (rfid, last_saved_session.rfid)
                        )

                self.logger.debug("Starting new charging session for rfid %s" % rfid)
                # Do not condense, an actual RFID was presented
                self.start_charge_session(
                        rfid=rfid,
                        condense=False
                        )
                start_session = True

            self.update_charger_and_led(start_session)


    # evse_reader_thread
    # rfid_reader_thread
    def start_charge_session(self, rfid, condense=False):
        self.logger.debug("start_charge_session() new charging session for rfid %s" % rfid)

        # Optimize: maybe get this from the latest db value rather than from the energy meter directly
        start_value = self.energy_util.getTotalKWHHValue()

        data_for_session = {
            "rfid"              : rfid, 
            "energy_device_id"  : self.device,
            "start_value"       : start_value,
            "tariff"            : ChargerConfigModel.get_config().charger_tariff,
            "end_value"         : start_value,
            "total_energy"      : 0,
            "total_price"       : 0
            }
        charge_session = ChargeSessionModel()
        charge_session.set(data_for_session)
        charge_session.save()
        rfid = RfidModel.get_one(rfid)
        if rfid.vehicle_make.upper() == "TESLA" and rfid.get_odometer: 
            # Try to add odometer
            self.save_tesla_values_in_thread(
                    charge_session_id=charge_session.id,
                    condense=condense
                    )
        # Emit websocket update
        if self.appSocketIO is not None:
            self.logger.debug(f'Send msg charge_session_started via websocket ...{charge_session.to_str()}')
            self.appSocketIO.emit(
                    'charge_session_started', 
                    { 
                        'id': WebAppConfig.ENERGY_DEVICE_ID,
                        'data': charge_session.to_str() 
                    }, 
                    namespace='/charge_session'
                    )


    # evse_reader_thread
    # rfid_reader_thread
    # lock threads before calling this
    def end_charge_session(self, charge_session):
        charge_session.end_value = self.energy_util.getTotalKWHHValue()
        charge_session.end_time = datetime.now()
        charge_session.total_energy = charge_session.end_value - charge_session.start_value
        charge_session.total_price = round(charge_session.total_energy * charge_session.tariff * 100) /100
        charge_session.save()
        # Emit websocket update
        if self.appSocketIO is not None:
            self.logger.debug(f'Send msg charge_session_ended via websocket ...{charge_session.to_str()}')
            self.appSocketIO.emit(
                    'charge_session_ended', 
                    { 
                        'id': WebAppConfig.ENERGY_DEVICE_ID,
                        'data': charge_session.to_str() 
                    }, 
                    namespace='/charge_session'
                    )


    # evse_reader_thread
    # rfid_reader_thread
    # charge_session_id is the row id in the database table
    def save_tesla_values_in_thread(self, charge_session_id, condense=False):
        uotu = UpdateOdometerTeslaUtil()
        uotu.set_charge_session_id(charge_session_id=charge_session_id)
        uotu.set_condense(condense=condense)
        # update_odometer takes some time, so put in own thread
        thread_for_tesla_util = threading.Thread(target=uotu.update_odometer, name='thread-tesla-util')
        thread_for_tesla_util.start()


    # rfid_reader_thread
    def has_rfid_open_session(self, rfid_latest_session):
        return (rfid_latest_session is not None and rfid_latest_session.end_time is None)


    # rfid_reader_thread
    def update_charger_and_led(self, start_session):
        if start_session:
            self.evse.switch_on()
            self.ledlighter.ready()
        else:
            self.evse.switch_off()
            self.ledlighter.available()


    def stop(self, block=False):
        self.logger.debug('Requested to stop')
        self.ledlighter.stop()
        self.stop_event.set()


    # evse_reader_thread
    def try_handle_charging(self, evse_state):
        try:
            self.handle_charging(evse_state)
        except Exception as e:
            self.logger.error("Error handle charging: %s", e, exc_info=True)
            self.ledlighter.error()


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
                if self.appSocketIO is not None:
                    self.logger.debug(f'Send msg charge_session_status_update via websocket ...{evse_state}')
                    self.appSocketIO.emit(
                            'charge_session_status_update', 
                            { 
                                'status': evse_state, 
                                'id': WebAppConfig.ENERGY_DEVICE_ID
                            }, 
                            namespace='/charge_session'
                            )
            if not self.ledlighter.is_charging_light_on():
                self.logger.debug('Start charging light pulse')
                self.ledlighter.charging()
        else:
            # self.logger.debug("Not charging")
            # Not charging. If it was charging, set light back to previous (before charging) light
            if self.is_status_charging:
                self.is_status_charging = False
                self.logger.debug("Charging is stopped")
                if self.appSocketIO is not None:
                    self.logger.debug(f'Send msg charge_session_status_update via websocket ...{evse_state}')
                    self.appSocketIO.emit(
                            'charge_session_status_update', 
                            {   # INACTIVE IS ALSO CONNECTED
                                'status': EvseState.EVSE_STATE_CONNECTED, 
                                'id': WebAppConfig.ENERGY_DEVICE_ID
                            }, 
                            namespace='/charge_session'
                            )
                if self.ledlighter.is_charging_light_on():
                    self.ledlighter.back_to_previous_light()


    # Auto Session starts a new session when the EVSE starts charging and during the set amount of minutes less
    # than the amount of energy has been consumed (auto was away)
    # A Tesla Model 3 75kWh Dual Motor charges 0.2kWh every 1:23h (16 feb 2020)
    # Only called upon switch from not-charging to chargin by the EVSE, so a session is ongoin
    # evse_reader_thread
    def handle_auto_session(self):
        self.logger.debug('handle_auto_session() enabled: {}'.format(WebAppConfig.autoSessionEnabled))
        # Open session, otherwise this method is not called
        if WebAppConfig.autoSessionEnabled: 
            edmm = EnergyDeviceMeasureModel()
            kwh_used = edmm.get_usage_since(
                    WebAppConfig.ENERGY_DEVICE_ID,
                    (datetime.today() - timedelta(minutes=WebAppConfig.autoSessionMinutes))
                    )
            if kwh_used > WebAppConfig.autoSessionEnergy:
                self.logger.debug('Keep the current session. More energy ({}kWh) used than {}kWh in {} minutes'
                           .format(
                                kwh_used,
                                WebAppConfig.autoSessionEnergy, 
                                WebAppConfig.autoSessionMinutes
                            )
                        )
            else:
                self.logger.info('Start a new session (auto-session). Less energy ({}kWh) used than {}kWh in {} minutes'
                           .format(
                                kwh_used,
                                WebAppConfig.autoSessionEnergy,
                                WebAppConfig.autoSessionMinutes
                            )
                        )
                with self.threadLock:
                    # Lock to prevent the session to be hijacked when someone simultaneously presents the rfid card
                    charge_session = ChargeSessionModel.get_open_charge_session_for_device(self.device)
                    self.end_charge_session(charge_session)
                    # Verify if the auto session was generated correctly. If the odometer value is equal, the session should be condensed
                    # Condense after the odometer update has completed! Done in the same thread
                    self.start_charge_session(
                            rfid=charge_session.rfid,
                            condense=WebAppConfig.autoSessionCondenseSameOdometer
                            )


    # rfid_reader_thread
    def buzz_ok(self):
        self.buzzer.buzz_other_thread(.1, 1)

    # rfid_reader_thread
    def buzz_error(self):
        self.buzzer.buzz_other_thread(.1, 2)

    # Callback from MeasureElectricityUsageThread with updated EnergyDeviceMeasureModel
    def energyUpdate(self, device_measurement):
        self.logger.debug('energyUpdate() callback...')
        # Open charge session for this energy device?
        with self.threadLock:
            open_charge_session_for_device = \
                ChargeSessionModel.get_open_charge_session_for_device(
                        device_measurement.energy_device_id
                )
            if open_charge_session_for_device != None:
                self.logger.debug('energyUpdate() open charge session, updating usage. device_measurement {}, open_charge_session_for_device {}'.format(str(device_measurement.to_str()), str(open_charge_session_for_device.to_str())))
                # Update session usage
                open_charge_session_for_device.end_value = device_measurement.kw_total
                self.logger.debug('energyUpdate() end_value to %s...' % open_charge_session_for_device.end_value)
                open_charge_session_for_device.total_energy = \
                    round((open_charge_session_for_device.end_value - open_charge_session_for_device.start_value) *10) /10
                self.logger.debug('energyUpdate() total_energy to %s...' % open_charge_session_for_device.total_energy)
                open_charge_session_for_device.total_price = \
                    round(open_charge_session_for_device.total_energy * open_charge_session_for_device.tariff * 100) /100 
                self.logger.debug('energyUpdate() total_price to %s...' % open_charge_session_for_device.total_price)
                open_charge_session_for_device.save() 
                # Emit changes via web socket
                if self.appSocketIO is not None:
                    self.counter += 1
                    self.logger.debug(f'Send msg {self.counter} for charge_session_data_update via websocket...')
                    self.appSocketIO.emit(
                            'charge_session_data_update', 
                            { 
                                'id': WebAppConfig.ENERGY_DEVICE_ID,
                                'data': open_charge_session_for_device.to_str() 
                            }, 
                            namespace='/charge_session'
                            )

