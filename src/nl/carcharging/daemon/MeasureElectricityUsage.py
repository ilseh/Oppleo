import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from injector import inject
from service import Service

from nl.carcharging.models.EnergyDeviceMeasureModel import EnergyDeviceMeasureModel
from nl.carcharging.models.EnergyDeviceModel import EnergyDeviceModel
from nl.carcharging.utils.EnergyUtil import EnergyUtil

PROCESS_NAME = 'measure_electricity_usage'
LOG_FILE = '/tmp/%s.log' % PROCESS_NAME

scheduler = BlockingScheduler()

# TODO: make pid_dir configurable
PID_DIR = '/tmp/'
SECONDS_IN_HOUR = 60 * 60


class MeasureElectricityUsage(Service):

    @inject
    def __init__(self):
        super(MeasureElectricityUsage, self).__init__(PROCESS_NAME, pid_dir=PID_DIR)

    def run(self):
        self.logger.debug('running')
        self.create_save_measurement_jobs()

    def create_save_measurement_jobs(self):
        measure_jobname_base = "measuring_%s"

        self.logger.info('Searching for measurement devices configured in the db')
        energy_devices = EnergyDeviceModel.get_all()
        self.logger.info('Found %d measurement devices' % len(energy_devices))

        for energy_device in energy_devices:
            self.logger.info('Found energy device %s, adding it to scheduler' % energy_device.energy_device_id)
            scheduler.add_job(id=measure_jobname_base % energy_device.energy_device_id,
                              func=try_handle_measurement, args=[EnergyUtil(), energy_device.energy_device_id],
                              trigger="interval", seconds=10)

        scheduler.start()

    def remove_measurement_jobs(self):
        self.logger.debug('stopping scheduled jobs')
        scheduler.remove_all_jobs()
        scheduler.shutdown()


def try_handle_measurement(energy_util: EnergyUtil, energy_device_id):
    try:
        handle_measurement(energy_util, energy_device_id)
    except Exception as e:
        logger = logging.getLogger(PROCESS_NAME)
        logger.error('Could not execute handle_measurement %s' % e)


def handle_measurement(energy_util: EnergyUtil, energy_device_id):
    logger = logging.getLogger(PROCESS_NAME)
    logger.debug("starting measure %s" % energy_device_id)

    data = energy_util.getMeasurementValue(energy_device_id)
    logger.debug('Measurement returned %s' % data)
    device_measurement = EnergyDeviceMeasureModel()
    device_measurement.set(data)

    logger.debug('New measurement values: %s, %s, %s' % (device_measurement.id, device_measurement.kw_total,
                                                         device_measurement.created_at))

    last_save_measurement = EnergyDeviceMeasureModel().get_last_saved(energy_device_id)

    if last_save_measurement is None:
        logger.info('No saved measurement found, is this the first run for device %s?' % energy_device_id)
    else:
        logger.debug(
            'Last save measurement values: %s, %s, %s' % (last_save_measurement.id, last_save_measurement.kw_total,
                                                          last_save_measurement.created_at))

    if last_save_measurement is None or is_a_value_changed(last_save_measurement, device_measurement) \
            or is_measurement_older_than_1hour(last_save_measurement, device_measurement):
        logger.debug('Measurement has changed or old one is older than 1 hour, saving it to db')
        device_measurement.save()
        logger.debug("value saved %s %s %s" %
                     (device_measurement.energy_device_id, device_measurement.id, device_measurement.created_at))
    else:
        logger.debug('Not saving new measurement because values of interest have not changed and last saved measurement'
                     ' is not older than 1 hour')


def is_a_value_changed(old_measurement, new_measurement):
    measurements_of_interest = {'kwh_l1', 'kwh_l2', 'kwh_l3', 'p_l1', 'p_l2', 'p_l3', 'a_l1', 'a_l2', 'a_l3',
                                'kw_total'}

    is_changed = False
    for measurement in measurements_of_interest:
        is_changed = getattr(new_measurement, measurement) != getattr(old_measurement, measurement)
        if is_changed:
            break

    return is_changed


def is_measurement_older_than_1hour(old_measurement, new_measurement):
    diff = new_measurement.created_at - old_measurement.created_at
    return (diff.seconds / SECONDS_IN_HOUR) > 1

