import logging
import signal
import threading
import time

from nl.carcharging.models.EnergyDeviceMeasureModel import EnergyDeviceMeasureModel
from nl.carcharging.config.WebAppConfig import WebAppConfig


class WebSocketThread(object):
    # Count the message updates send through the websocket
    counter = 1
    most_recent = ""
    app = None
    stop_event = None

    def __init__(self):
        self.logger = logging.getLogger('nl.carcharging.models.SessionModel')
        self.logger.debug('Initializing SessionModel without data')
        self.thread = None
        self.stop_event = threading.Event()

    def stop(self):
        self.logger.debug('Requested to stop')
        self.stop_event.set()

    def websocket_start(self):
        global WebAppConfig
        self.logger.debug('Starting background task...')
        lastRun = 0
        while not self.stop_event.is_set():
            # Sleep is interruptable by other threads, but sleeing 7 seconds before checking if 
            # stop is requested is a bit long, so sleep for 0.1 seconds, then check passed time
            if (time.time() *1000.0) > (lastRun + (WebAppConfig.device_measurement_check_interval *1000.0)):
                # time to run again
                try:
                    self.websocket_send_usage_update("status_update")
                except OperationalError as e:
                    # If the database is unavailable (or no access allowed),
                    # remain running untill the access is restored
                    self.logger.debug(f'Something wrong with the database! {e}')
                lastRun = time.time() *1000.0
            self.app.sleep(0.1)
        self.logger.debug(f'Terminating thread')
        # Releasing session if applicable
        db_session = DbSession()
        if (db_session is not None):
            self.logger.debug(f'Closimg DbSession on this thread...')
            db_session.remove()

    def start(self, app):
        self.stop_event.clear()
        self.logger.debug('Launching background task...')
        self.app = app
        self.logger.debug('start_background_task()')
        self.thread = self.app.start_background_task(self.websocket_start)

    def websocket_send_usage_update(self, type):
        global WebAppConfig
        self.logger.debug('Checking usage data...')

        device_measurement = EnergyDeviceMeasureModel()  
        device_measurement.energy_device_id = WebAppConfig.ENERGY_DEVICE_ID # "laadpaal_noord"
        qr = device_measurement.get_last_saved(energy_device_id=WebAppConfig.ENERGY_DEVICE_ID)
        if (self.most_recent != qr.get_created_at_str()):
            self.logger.debug(f'Send msg {self.counter} via websocket...')
            self.app.emit('status_update', { 'data': qr.to_str() }, namespace='/usage')
            self.most_recent = qr.get_created_at_str()
        else:
            self.logger.debug('No change in usage at this time.')

        self.counter += 1

    def wait(self):
        self.thread.join()
