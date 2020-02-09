import time
import logging

from nl.carcharging.models.EnergyDeviceMeasureModel import EnergyDeviceMeasureModel

class EnergyDevice():
    logger = None
    energy_device_id = None
    energuUtil = None
    interval = 10 # default value
    lastRun = 0


    def __init__(self, energy_device_id=None, interval=10, energyUtil=None):
        self.logger = logging.getLogger('nl.carcharging.daemon.EnergyDevice')
        self.logger.setLevel(logging.INFO)
        self.energy_device_id = energy_device_id
        self.interval = interval
        self.energyUtil = energyUtil


    def handleIfTimeTo(self):
        self.logger.debug(f'handleIfTimeTo() {self.energy_device_id}')
        if (time.time() *1000.0) > (self.lastRun + (self.interval *1000.0)):
            # time to run again
            self.logger.debug(f'handleIfTimeTo() - time to handle {self.energy_device_id}')
            try:
                self.handle()
            except Exception as e:
                self.logger.debug(f'Could not monitor energy device {self.energy_device_id}! {e}')
            self.lastRun = time.time() *1000.0
        else:
            self.logger.debug(f'handleIfTimeTo() - not yet time to handle {self.energy_device_id}')


    def handle(self):
        self.logger.debug("Start measure %s" % self.energy_device_id)

        data = self.energyUtil.getMeasurementValue(self.energy_device_id)
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
        else:
            self.logger.debug('Not saving new measurement because values of interest have not changed and last saved measurement'
                        ' is not older than 1 hour')


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

