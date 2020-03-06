import time
import logging

from nl.oppleo.models.EnergyDeviceMeasureModel import EnergyDeviceMeasureModel
from nl.oppleo.utils.GenericUtil import GenericUtil
from nl.oppleo.utils.WebSocketUtil import WebSocketUtil


SECONDS_IN_HOUR = 60 * 60

class EnergyDevice():
    counter = 0
    logger = None
    energy_device_id = None
    energyUtil = None
    modbusInterval = 10 # default value
    lastRun = 0
    appSocketIO = None
    callbackList = []


    def __init__(self, energy_device_id=None, modbusInterval=10, energyUtil=None, appSocketIO=None):
        self.logger = logging.getLogger('nl.oppleo.daemon.EnergyDevice')
        self.logger.setLevel(logging.DEBUG)
        self.energy_device_id = energy_device_id
        self.modbusInterval = modbusInterval
        self.energyUtil = energyUtil
        self.appSocketIO = appSocketIO
        

    def handleIfTimeTo(self):
        # self.logger.debug(f'handleIfTimeTo() {self.energy_device_id}')
        if (time.time() *1000.0) > (self.lastRun + (self.modbusInterval *1000.0)):
            # time to run again
            self.logger.debug(f'handleIfTimeTo() - time to handle {self.energy_device_id}')
            try:
                self.handle()
            except Exception as e:
                self.logger.debug(f'Could not monitor energy device {self.energy_device_id}! {e}')
            self.lastRun = time.time() *1000.0
        else:
            # self.logger.debug(f'handleIfTimeTo() - not yet time to handle {self.energy_device_id}')
            pass

    def handle(self):
        self.logger.debug("Start measure %s" % self.energy_device_id)

        data = self.energyUtil.getMeasurementValue()
        self.logger.debug('Measurement returned %s' % str(data))
        device_measurement = EnergyDeviceMeasureModel()
        device_measurement.set(data)

        self.logger.debug('New measurement values: %s, %s, %s' % (device_measurement.id, device_measurement.kw_total,
                                                            device_measurement.created_at))

        last_save_measurement = EnergyDeviceMeasureModel().get_last_saved(self.energy_device_id)

        if last_save_measurement is None:
            self.logger.info('No saved measurement found, is this the first run for device %s?' % self.energy_device_id)
        else:
            self.logger.debug(
                'Last save measurement values: %s, %s, %s' % (last_save_measurement.id, last_save_measurement.kw_total,
                                                            last_save_measurement.created_at))

        if last_save_measurement is None or self.is_a_value_changed(last_save_measurement, device_measurement) \
                or self.is_measurement_older_than_1hour(last_save_measurement, device_measurement):
            self.logger.debug('Measurement has changed or old one is older than 1 hour, saving it to db (if env=Production)')
            if GenericUtil.isProd():
                device_measurement.save()
                self.logger.debug("value saved %s %s %s" %
                        (device_measurement.energy_device_id, device_measurement.id, device_measurement.created_at))
            if self.appSocketIO is not None:
                # Emit as web socket update
                self.counter += 1
                self.logger.debug(f'Queue msg {self.counter} to be send via websocket ...{device_measurement.to_str()}')
                # Info heeft actuele kWh meter gegevens, geen laadpas info, dus public
                WebSocketUtil.emit(
                        event='status_update', 
                        data=device_measurement.to_str(), 
                        namespace='/usage',
                        public=True
                    )

            # Callbacks to notify update
            self.callback(device_measurement)
        else:
            self.logger.debug('Not saving new measurement, no signbificant change and not older than 1 hour')


    def is_a_value_changed(self, old_measurement, new_measurement):
        measurements_of_interest = {'kwh_l1', 'kwh_l2', 'kwh_l3', 'p_l1', 'p_l2', 'p_l3', 'a_l1', 'a_l2', 'a_l3',
                                    'kw_total'}

        for measurement in measurements_of_interest:
            if getattr(new_measurement, measurement) != getattr(old_measurement, measurement):
                return True
        # Not changed
        return False


    def is_measurement_older_than_1hour(self, old_measurement, new_measurement):
        diff = new_measurement.created_at - old_measurement.created_at
        return (diff.seconds / SECONDS_IN_HOUR) > 1

    # Callbacks called when new values are read
    def addCallback(self, fn):
        self.logger.debug('EnergyDevice.addCallback()')
        self.callbackList.append(fn)
        
    # Callbacks to notify update
    def callback(self, device_measurement):
        self.logger.debug('EnergyDevice.callback()')
        for callbackFn in self.callbackList:
            self.logger.debug('EnergyDevice.callback() calling')
            callbackFn(device_measurement)

