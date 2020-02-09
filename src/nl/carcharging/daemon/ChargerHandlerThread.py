import sys
import threading
import time
import logging
from datetime import datetime

from injector import inject
from service import Service

from nl.carcharging.models.ChargeSessionModel import ChargeSessionModel
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
    app = None
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
    tesla_util = None
    is_status_charging = False
    device = None

    def __init__(self, energy_util: EnergyUtil, charger: Charger, ledlighter: LedLighter, buzzer: Buzzer, evse: Evse,
                 evse_reader: EvseReader, tesla_util: UpdateOdometerTeslaUtil):
        self.logger = logging.getLogger('nl.carcharging.daemon.ChargerHandlerThread')
        self.logger.setLevel(logging.INFO)
        self.evse_reader_thread = None
        self.rfid_reader_thread = None
        self.stop_event = threading.Event()
        self.energy_util = energy_util
        self.charger = charger
        self.ledlighter = ledlighter
        self.buzzer = buzzer
        self.evse = evse
        self.evse_reader = evse_reader
        self.tesla_util = tesla_util
        self.is_status_charging = False


    def start(self, app):
        self.stop_event.clear()
        self.logger.debug('Launching background task...')
        self.app = app
        self.device = GenericUtil.getMeasurementDevice()
        self.logger.debug('start_background_task() - evseReaderLoop')
        self.evse_reader_thread = self.app.start_background_task(self.evseReaderLoop)
        self.logger.debug('start_background_task() - rfidReaderLoop')
        self.rfid_reader_thread = self.app.start_background_task(self.rfidReaderLoop)
        self.logger.debug('Done starting rfid reader and evse reader backgroubd tasks')


    def stop(self):
        self.logger.debug('Requested to stop')
        self.stop_event.set()


    def evseReaderLoop(self):
        # Redirect stdout to logfile
        try:
            # Assume first logger handler is the correct file to route stdout to.
#            sys.stdout = open(self.logger.handlers[0].baseFilename, 'a')
            sys.stdout = open('/tmp/stdout.log', 'a')
#            sys.stdout = open('/home/pi/stdout.log', 'a')

            self.evse_reader.loop(self.stop_event.is_set, lambda evse_state: self.try_handle_charging(evse_state))

        except Exception as ex:
            self.logger.exception('Could not start evse reader loop')
            self.ledlighter.error()
        finally:
            print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> flushing stdout', flush=True)


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
        except Exception as ex:
            self.logger.error("Could not authorize %s %s" % (rfid, ex))

        if not is_authorized:
            raise NotAuthorizedException("Unauthorized rfid %s" % rfid)
        if is_expired:
            raise ExpiredException("Rfid isn't valid yet/anymore. Valid from %s to %s" %
                                   (rfid_data.valid_from, rfid_data.valid_until))

    def is_expired(self, from_date, until_date):

        expired = False
        if from_date:
            expired = datetime.now() < from_date

        if not expired and until_date:
            expired = datetime.now() > until_date

        return expired


    def resume_session_if_applicable(self, device):
        # Check if there was a session active when this daemon was stopped.
        last_saved_session = ChargeSessionModel.get_latest_charge_session(device)

        if last_saved_session and last_saved_session.end_time is None:
            self.logger.info("After startup continuing an active session for rfid %s" % last_saved_session.rfid)
            resume_session = True
        else:
            resume_session = False
        self.update_charger_and_led(resume_session)


    def rfidReaderLoop(self):
        self.resume_session_if_applicable(self.device)
        reader = RfidReader()
        while not self.stop_event.is_set():
            try:
                self.read_rfid(reader, self.device)
            except Exception as ex:
                self.logger.error("Could not execute run_read_rfid: %s" % ex)
                self.buzz_error()
                self.ledlighter.error(duration=.6)
            time.sleep(.25)
        self.logger.info("Stopping RfidReader")


    def is_other_session_active(self, last_saved_session, rfid):
        return last_saved_session and not last_saved_session.end_value \
               and last_saved_session.rfid != str(rfid)

    def read_rfid(self, reader, device):
        self.logger.info("Starting rfid reader for device %s" % device)
        rfid, text = reader.read()
        self.logger.debug("Rfid id and text: %d - %s" % (rfid, text))

        rfid_latest_session = ChargeSessionModel.get_latest_charge_session(device, rfid)

        start_session = False
        data_for_session = {"rfid": rfid, "energy_device_id": device}
        # If rfid has open session, no need to authorize, let it end the session.
        # If no open session, authorize rfid.
        if self.has_rfid_open_session(rfid_latest_session):
            self.buzz_ok()
            self.logger.debug("Stopping charging session for rfid %s" % rfid)
            self.end_charge_session(rfid_latest_session, device)
        else:
            self.authorize(rfid)
            self.buzz_ok()

            # If there is an open session for another rfid, raise error.
            last_saved_session = ChargeSessionModel.get_latest_charge_session(device)
            if self.is_other_session_active(last_saved_session, rfid):
                raise OtherRfidHasOpenSessionException(
                    "Rfid %s was offered but rfid %s has an open session" % (rfid, last_saved_session.rfid)
                    )

            self.logger.debug("Starting new charging session for rfid %s" % rfid)
            self.start_charge_session(rfid, device)
            self.save_tesla_values_in_thread(charge_session_id=session.id)
            start_session = True

        self.update_charger_and_led(start_session)


    def start_charge_session(self, rfid, device):
        data_for_session = {
            "rfid"              : rfid, 
            "energy_device_id"  : device,
            "start_value"       : self.energy_util.getMeasurementValue(device).get('kw_total'),
            "tariff"            : ChargerConfigModel.get_config().charger_tariff,
            "end_value"         : self.energy_util.getMeasurementValue(device).get('kw_total'),
            "total_energy"      : 0,
            "total_price"       : 0
            }
        session = ChargeSessionModel()
        session.set(data_for_session)
        session.save()
        rfid = RfidModel.get_one(rfid)
        if rfid.vehicle_make.upper() == "TESLA" and rfid.get_odometer: 
            # Try to add odometer
            self.save_tesla_values_in_thread(charge_session_id=session.id)


    def end_charge_session(self, charge_session, device):
        charge_session.end_value = self.energy_util.getMeasurementValue(device)['kw_total']
        charge_session.end_time = datetime.now()
        charge_session.total_energy = charge_session.end_value - charge_session.start_value
        charge_session.total_price = round(charge_session.total_energy * charge_session.tariff * 100) /100
        charge_session.save()


    def save_tesla_values_in_thread(self, charge_session_id):
        self.tesla_util.set_charge_session_id(charge_session_id=charge_session_id)
        # update_odometer takes some time, so put in own thread
        thread_for_tesla_util = threading.Thread(target=self.tesla_util.update_odometer, name='thread-tesla-util')
        thread_for_tesla_util.start()


    def has_rfid_open_session(self, rfid_latest_session):
        return not (rfid_latest_session is None or rfid_latest_session.end_value)


    def update_charger_and_led(self, start_session):
        if start_session:
            self.evse.switch_on()
            self.ledlighter.ready()
        else:
            self.evse.switch_off()
            self.ledlighter.available()

    def stop(self, block=False):
        self.ledlighter.stop()

    def try_handle_charging(self, evse_state):
        try:
            self.handle_charging(evse_state)
        except Exception as ex:
            self.logger.error("Error handle charging: %s", ex)
            self.ledlighter.error()

    def handle_charging(self, evse_state):
        if evse_state == EvseState.EVSE_STATE_CHARGING:
            self.logger.debug("Device is currently charging")
            self.is_status_charging = True
            if not self.ledlighter.is_charging_light_on():
                self.logger.debug('Start charging light pulse')
                self.ledlighter.charging()
        else:
            self.logger.debug("Not charging")
            # Not charging. If it was charging, set light back to previous (before charging) light
            if self.is_status_charging:
                self.is_status_charging = False
                self.logger.debug("Charging is stopped")
                if self.ledlighter.is_charging_light_on():
                    self.ledlighter.back_to_previous_light()

    def buzz_ok(self):
        self.buzzer.buzz_other_thread(.1, 1)

    def buzz_error(self):
        self.buzzer.buzz_other_thread(.1, 2)

