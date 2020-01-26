import logging
import signal

from nl.carcharging.models.EnergyDeviceMeasureModel import EnergyDeviceMeasureModel
from nl.carcharging.config.WebAppConfig import WebAppConfig


class WebSocketThread(object):
    # Count the message updates send through the websocket
    counter = 1
    most_recent = ""
    sigterm = False
    app = None

    def __init__(self):
        self.logger = logging.getLogger('nl.carcharging.models.SessionModel')
        self.logger.debug('Initializing SessionModel without data')
        self.thread = None

    def websocket_start(self):
        self.logger.debug('Starting background task...')
        while not self.sigterm:
            self.app.sleep(WebAppConfig.device_measurement_check_interval)
            try:
                self.websocket_send_usage_update("status_update")
            except OperationalError as e:
                # If the database is unavailable (or no access allowed),
                # remain running untill the access is restored
                self.logger.debug(f'Something wrong with the database! {e}')
        self.logger.debug(f'Terminating thread')

    def sig_handler(self, signum, frame):
        self.logger.debug('Termination signalled ({})...'.format(signum))
        self.sigterm = True

    def start(self, app):
        self.logger.debug('Launching background task...')
        self.app = app
        signal.signal(signal.SIGTERM, self.sig_handler)
        signal.signal(signal.SIGINT, self.sig_handler)
        self.thread = self.app.start_background_task(self.websocket_start)

    def websocket_send_usage_update(self, type):
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
