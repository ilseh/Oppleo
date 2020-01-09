import logging
import os
import sys
import time
from datetime import datetime

from nl.carcharging.models.EnergyDeviceMeasureModel import EnergyDeviceMeasureModel
from nl.carcharging.models.RfidModel import RfidModel
from nl.carcharging.models.SessionModel import SessionModel
from nl.carcharging.services.Buzzer import Buzzer
from nl.carcharging.services.Charger import Charger
from nl.carcharging.utils.GenericUtil import GenericUtil

try:
    import RPi.GPIO as GPIO
    from mfrc522 import SimpleMFRC522
except RuntimeError:
    logging.debug('Assuming dev env')

from apscheduler.schedulers.background import BackgroundScheduler
from injector import inject, Injector
from service import Service

from nl.carcharging.config import Logger

from nl.carcharging.services.LedLighter import LedLighter
from nl.carcharging.services.RfidReader import RfidReader
from nl.carcharging.utils.EnergyUtil import EnergyUtil

PROCESS_NAME = 'rfid_reader'
LOG_FILE = '/tmp/%s.log' % PROCESS_NAME

MAX_SECONDS_INTERVAL_CHARGING = 20

scheduler = BackgroundScheduler()

# TODO: make pid_dir configurable
PID_DIR = '/tmp/'
SECONDS_IN_HOUR = 60 * 60
LIGHT_INTENSITY_LOW = 5
LIGHT_INTENSITY_HIGH = 90


class NotAuthorizedException(Exception):
    pass

class OtherRfidHasOpenSessionException(Exception):
    pass

class ExpiredException(Exception):
    pass

class LedLightHandler(Service):

    @inject
    def __init__(self, energy_util: EnergyUtil, charger: Charger):
        super(LedLightHandler, self).__init__(PROCESS_NAME, pid_dir=PID_DIR)

        self.energy_util = energy_util
        self.charger = charger
        self.buzzer = Buzzer()

        self.ledlighterAvailable = LedLighter(LedLighter.LED_GREEN)
        self.ledlighterReady = LedLighter(LedLighter.LED_RED, LedLighter.LED_GREEN)
        self.ledlighterCharging = LedLighter(LedLighter.LED_BLUE)
        self.ledlighterError = LedLighter(LedLighter.LED_RED)

        self.current_light = None
        self.previous_light = None

    def error_status(self):
        self.current_light = self.ledlighterError
        self.current_light.on(80)

    def run(self):

        device = GenericUtil.getMeasurementDevice()

        try:
            scheduler.add_job(id="check_is_charging",
                              func=self.try_handle_charging, args=[device],
                              trigger="interval", seconds=10)
            scheduler.start()
        except Exception as ex:
            self.logger.error("Could not start scheduler to check if charging is active: %s" % ex)
            self.error_status()

        try:
            self.read_rfid_loop(device)
        except Exception as ex:
            self.logger.error("Could not execute read_rfid_loop %s" % ex)
            self.error_status()

    def authorize(self, rfid):

        is_authorized = False
        is_expired = False
        try:
            rfid_data = RfidModel.get_one(rfid)
            if rfid_data is None:
                self.logger.warn("Unknown rfid offered. Access denied and rfid value saved in db.")
                new_rfid_entry = RfidModel({"rfid": rfid})
                new_rfid_entry.save()
            else:
                is_authorized = rfid_data.allow
                is_expired = self.is_expired(rfid_data.valid_from, rfid_data.valid_until)
                rfid_data.last_used_at = datetime.now()
                rfid_data.save()
        except Exception as ex:
            self.logger.error("Could not authorize %s %s" % (rfid, ex))

        if not is_authorized:
            self.buzz_error()
            raise NotAuthorizedException("Unauthorized rfid %s" % rfid)
        if is_expired:
            self.buzz_error()
            raise ExpiredException("Rfid isn't valid yet/anymore. Valid from %s to %s" %
                                   (rfid_data.valid_from, rfid_data.valid_until))

        self.buzz_ok()

    def is_expired(self, from_date, until_date):

        expired = False
        if from_date:
            expired = datetime.now() < from_date

        if not expired and until_date:
            expired = datetime.now() > until_date

        return expired

    def temp_switch_to_light(self, light, brightness, duration):
        self.previous_light = self.current_light
        self.current_light.off()
        self.current_light = light
        self.current_light.on(brightness)
        time.sleep(duration)
        self.current_light.off()
        self.current_light = self.previous_light
        self.current_light.on(self.current_light.brightness)

    def resume_session_if_applicable(self, device):
        # Check if there was a session active when this daemon was stopped.
        last_saved_session = SessionModel.get_latest_rfid_session(device)

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
                self.logger.error("Could not execute run_rfid: %s" % ex)
                self.temp_switch_to_light(self.ledlighterError, LIGHT_INTENSITY_HIGH, duration=3)

            time.sleep(2)
        else:
            self.logger.info("Stopping RfidReader")
            self.stop()

    def is_other_pending_session(self, last_saved_session, rfid):
        return last_saved_session and not last_saved_session.end_value \
               and last_saved_session.rfid != str(rfid)

    def read_rfid(self, reader, device):
        self.logger.info("Starting rfid reader for device %s" % device)
        rfid, text = reader.read()
        self.logger.debug("Rfid id and text: %d - %s" % (rfid, text))

        rfid_latest_session = SessionModel.get_latest_rfid_session(device, rfid)

        start_session = False
        data_for_session = {"rfid": rfid, "energy_device_id": device}
        # If rfid has open session, no need to authorize, let it end the session.
        # If no open session, authorize rfid.
        if self.has_rfid_open_session(rfid_latest_session):
            self.buzz_ok()
            self.logger.debug("Stopping charging session for rfid %s" % rfid)
            rfid_latest_session.end_value = self.energy_util.getMeasurementValue(device)['kw_total']
            rfid_latest_session.save()
        else:
            self.authorize(rfid)

            # If there is an open session for another rfid, raise error.
            last_saved_session = SessionModel.get_latest_rfid_session(device)
            if self.is_other_pending_session(last_saved_session, rfid):
                raise OtherRfidHasOpenSessionException(
                    "Rfid %s was offered but rfid %s has an open session" % (rfid, last_saved_session.rfid))

            self.logger.debug("Starting new charging session for rfid %s" % rfid)
            data_for_session['start_value'] = self.energy_util.getMeasurementValue(device).get('kw_total')
            session = SessionModel(data_for_session)
            session.save()
            start_session = True

        self.update_charger_and_led(start_session)

    def has_rfid_open_session(self, rfid_latest_session):
        return not (rfid_latest_session is None or rfid_latest_session.end_value)

    def update_charger_and_led(self, start_session):
        if self.current_light:
            self.turn_current_light_off()
        if start_session:
            self.charger.start()
            self.current_light = self.ledlighterReady
        else:
            self.charger.stop()
            self.current_light = self.ledlighterAvailable
        self.current_light.on(LIGHT_INTENSITY_LOW)

    def turn_current_light_off(self):
        if self.current_light == self.ledlighterCharging:
            self.current_light.pulse_stop()
        else:
            self.current_light.off()

    def stop(self, block=False):
        lights = {self.ledlighterAvailable, self.ledlighterReady, self.ledlighterError}
        for light in lights:
            light.off()
            light.cleanup()

    def try_handle_charging(self, device):
        try:
            self.handle_charging(device)
        except Exception as ex:
            self.error_status()

    def handle_charging(self, device):

        if self.is_car_charging(device):
            self.logger.debug("Device is currently charging")
            if self.current_light != self.ledlighterCharging:
                self.previous_light = self.current_light
                self.turn_current_light_off()
                self.logger.debug("Prevous light off, setting charging light")
                self.current_light = self.ledlighterCharging
                self.logger.debug('Start charging light pulse')
                self.current_light.pulse()
        else:
            self.logger.debug("Not charging")
            # Not charging. If it was charging, set light back to previous light
            if self.current_light == self.ledlighterCharging:
                self.logger.debug("Charging is stopped, setting back previous light %s" % self.previous_light)
                self.turn_current_light_off()
                self.current_light = self.previous_light
                self.current_light.on(LIGHT_INTENSITY_LOW)

    def is_car_charging(self, device):
        last_two_measures = EnergyDeviceMeasureModel().get_last_n_saved(device, 2)
        diff_last_two_measures_saved = last_two_measures[0].created_at - last_two_measures[1].created_at
        # Get dummy measure to get current datetime (make sure the datetime is calculated like in the saved sessions)
        # which we can use to see if charging is going on.
        current_date_time = EnergyDeviceMeasureModel()
        current_date_time.set({})
        diff_now_and_last_saved_session = current_date_time.created_at - last_two_measures[0].created_at
        return diff_now_and_last_saved_session.seconds <= MAX_SECONDS_INTERVAL_CHARGING \
               and diff_last_two_measures_saved.seconds <= MAX_SECONDS_INTERVAL_CHARGING

    def buzz_ok(self):
        self.buzzer.buzz(.5, 1)

    def buzz_error(self):
        self.buzzer.buzz(.5, 2)

def main():
    Logger.init_log(PROCESS_NAME, LOG_FILE)

    env_name = os.getenv('CARCHARGING_ENV')

    logger = logging.getLogger(PROCESS_NAME)
    logger.info('Starting for environment %s' % env_name)

    if len(sys.argv) != 2:
        sys.exit('Invalid COMMAND %s, give an argument, ie \'start\'' % sys.argv[0])

    cmd = sys.argv[1].lower()

    logger.info('Received command: %s' % cmd)

    injector = Injector()
    service = injector.get(LedLightHandler)

    if cmd == 'start':
        service.start()
        logger.debug('started')
    elif cmd == 'debug':
        service.run()
    elif cmd == 'stop':
        stopped = service.stop()
        if not stopped:
            sys.exit('Could not stop service, trying kill instead')
    elif cmd == 'kill':
        # GPIO.cleanup()
        stopped = service.kill()
    elif cmd == 'status':
        if service.is_running():
            print("Service is running.")
        else:
            print("Service is not running.")
    else:
        sys.exit('Unknown command "%s".' % cmd)


if __name__ == '__main__':
    main()
