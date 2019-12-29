from logging.handlers import SysLogHandler

from service import find_syslog, Service
from injector import inject, Injector
from apscheduler.schedulers.blocking import BlockingScheduler
from nl.carcharging.services.EnergyUtil import EnergyUtil
from nl.carcharging.models.EnergyDeviceModel import EnergyDeviceModel
from nl.carcharging.models.EnergyDeviceMeasureModel import EnergyDeviceMeasureModel

import os
import logging
import sys
import signal

PROCESS_NAME = 'measure_electricity_usage'
LOG_FILE = '/tmp/measure_electricity_usage.log'

def init_log():
    logger_daemon = logging.getLogger(PROCESS_NAME)
    logger_package = logging.getLogger('nl.charging')
    logger_package.setLevel(logging.DEBUG)
    logger_daemon.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler(LOG_FILE)
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s -  %(threadName)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger_package.addHandler(fh)
    logger_daemon.addHandler(fh)
    logger_package.addHandler(ch)
    logger_daemon.addHandler(ch)



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
    device_measurement = EnergyDeviceMeasureModel(data)

    logger.debug('New measurement values: %s, %s, %s' % (device_measurement.id, device_measurement.kw_total,
                                                         device_measurement.created_at))

    last_save_measurement = EnergyDeviceMeasureModel.get_last_one()

    if last_save_measurement is None:
        logger.info('No saved measurement found, is this the first run for device %s?' % energy_device_id)
    else:
        logger.debug('Last save measurement values: %s, %s, %s' % (last_save_measurement.id, last_save_measurement.kw_total,
                                                                   last_save_measurement.created_at))


    if last_save_measurement is None or is_a_value_changed(last_save_measurement, device_measurement) \
            or is_measurement_older_than_1hour(last_save_measurement, device_measurement):
        logger.debug('Measurement has changed or old one is older than 1 hour, saving it to db')
        save_measurement(device_measurement)
    else:
        logger.debug('Not saving new measurement because values of interest have not changed and last saved measurement'
                     ' is not older than 1 hour')


def save_measurement(device_measurement):
    logger = logging.getLogger(PROCESS_NAME)
    logger.debug('want to save %s %s %s' %
                  (device_measurement.energy_device_id, device_measurement.id, device_measurement.created_at))
    device_measurement.save()
    logger.debug("value saved %s %s %s" %
                  (device_measurement.energy_device_id, device_measurement.id, device_measurement.created_at))


def is_a_value_changed(old_measurement, new_measurement):
    measurements_of_interest = {'kwh_l1', 'kwh_l2', 'kwh_l3', 'p_l1', 'p_l2', 'p_l3', 'a_l1', 'a_l2', 'a_l3', 'kw_total'}

    for measurement in measurements_of_interest:
        is_changed = getattr(new_measurement, measurement) > getattr(old_measurement, measurement)
        if is_changed:
            break

    return is_changed


def is_measurement_older_than_1hour(old_measurement, new_measurement):
    diff = new_measurement.created_at - old_measurement.created_at
    return (diff.seconds / SECONDS_IN_HOUR) > 1


def main():
    init_log()
    # logging.basicConfig(filename="/tmp/measurement_daemon.log")
    # logging.basicConfig(level=logging.DEBUG)
    # logging.basicConfig(filename='example.log', level=logging.NOTSET)

    # logger = logging.getLogger('measure_electricity_usage_daemon')

    env_name = os.getenv('CARCHARGING_ENV')

    logger = logging.getLogger(PROCESS_NAME)
    logger.info('Starting for environment %s' % env_name)

    if len(sys.argv) != 2:
        sys.exit('Invalid COMMAND %s, give an argument, ie \'start\'' % sys.argv[0])

    cmd = sys.argv[1].lower()

    injector = Injector()
    service = injector.get(MeasureElectricityUsage)

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
