import sys
import threading
import time
from datetime import datetime

from injector import inject
from service import Service

from nl.oppleo.exceptions.Exceptions import (NotAuthorizedException, 
                                             OtherRfidHasOpenSessionException, 
                                             ExpiredException)

from nl.oppleo.config.OppleoConfig import OppleoConfig
from nl.oppleo.models.ChargeSessionModel import ChargeSessionModel
from nl.oppleo.models.RfidModel import RfidModel
from nl.oppleo.services.Buzzer import Buzzer
from nl.oppleo.services.Evse import Evse
from nl.oppleo.services.EvseReader import EvseReader
from nl.oppleo.services.EvseReaderProd import EvseState
from nl.oppleo.services.RfidReader import RfidReader
from nl.oppleo.utils.GenericUtil import GenericUtil
from nl.oppleo.utils.UpdateOdometerTeslaUtil import UpdateOdometerTeslaUtil

GenericUtil.importGpio()
GenericUtil.importMfrc522()


PROCESS_NAME = 'rfid_reader'

# TODO: make pid_dir configurable
PID_DIR = '/tmp/'
SECONDS_IN_HOUR = 60 * 60


class LedLightHandler(Service):

    @inject
    def __init__(self, energy_util, ledlighter, buzzer, evse,
                 evse_reader, tesla_util):
        super(LedLightHandler, self).__init__(PROCESS_NAME, pid_dir=PID_DIR)

        self.energy_util = energy_util
        self.ledlighter = ledlighter
        self.buzzer = buzzer
        self.evse = evse
        self.evse_reader = evse_reader
        self.tesla_util = tesla_util
        self.is_status_charging = False

    def run(self):

        oppleoConfig = OppleoConfig()
        device = oppleoConfig.chargerName

        try:
            self.start_evse_reader_loop_in_thread()
        except Exception as ex:
            self.logger.error("Could not start service to check if charging is active: %s" % ex)
            self.ledlighter.error()

        try:
            self.read_rfid_loop(device)
        except Exception as ex:
            self.logger.error("Could not execute read_rfid_loop %s" % ex)
            self.buzz_error()
            self.ledlighter.error()

    def start_evse_reader_loop_in_thread(self):
        thread_for_evse_reader = threading.Thread(target=self.start_evse_reader_loop, name='EvseLedReaderThread')
        thread_for_evse_reader.start()

    def start_evse_reader_loop(self):
        # Redirect stdout to logfile
        try:
            # Assume first logger handler is the correct file to route stdout to.
            sys.stdout = open(self.logger.handlers[0].baseFilename, 'a')

            self.evse_reader.loop(self.got_sigterm, lambda evse_state: self.try_handle_charging(evse_state))
        except Exception as ex:
            self.logger.exception('Could not start evse reader loop')
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

        if last_saved_session and last_saved_session.end_value is None:
            self.logger.info("After startup continuing an active session for rfid %s" % last_saved_session.rfid)
            resume_session = True
        else:
            resume_session = False
        self.update_charger_and_led(resume_session)

    def read_rfid_loop(self, device):

        self.resume_session_if_applicable(device)

        reader = RfidReader()
        while not self.got_sigterm():
            try:
                self.read_rfid(reader, device)
            except Exception as ex:
                self.logger.error("Could not execute run_read_rfid: %s" % ex)
                self.buzz_error()
                self.ledlighter.error(duration=3)

            time.sleep(2)
        else:
            self.logger.info("Stopping RfidReader")
            self.stop()

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
            rfid_latest_session.end_value = self.energy_util.getMeasurementValue(device)['kw_total']
            rfid_latest_session.end_time = datetime.now()
            rfid_latest_session.save()
        else:
            self.authorize(rfid)
            self.buzz_ok()

            # If there is an open session for another rfid, raise error.
            last_saved_session = ChargeSessionModel.get_latest_charge_session(device)
            if self.is_other_session_active(last_saved_session, rfid):
                raise OtherRfidHasOpenSessionException(
                    "Rfid %s was offered but rfid %s has an open session" % (rfid, last_saved_session.rfid))

            self.logger.debug("Starting new charging session for rfid %s" % rfid)
            data_for_session['start_value'] = self.energy_util.getMeasurementValue(device).get('kw_total')
            session = ChargeSessionModel()
            session.set(data_for_session)
            session.save()
            self.save_tesla_values_in_thread(charge_session_id=session.id)
            start_session = True

        self.update_charger_and_led(start_session)

    def save_tesla_values_in_thread(self, charge_session_id):
        self.tesla_util.set_charge_session_id(charge_session_id=charge_session_id)
        # update_odometer takes some time, so put in own thread
        thread_for_tesla_util = threading.Thread(target=self.tesla_util.update_odometer, name='TeslaUtilThread')
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

