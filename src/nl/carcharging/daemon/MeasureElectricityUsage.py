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


scheduler = BlockingScheduler()

# TODO: make name and pid_dir configurable
PROCESS_NAME = 'measure_electricity_usage'
PID_DIR = '/tmp'

# logging.basicConfig(level=logging.DEBUG, filename="/tmp/DaemonMeasureElectricity.log")


class MeasureElectricityUsage(Service):

    @inject
    def __init__(self, energyUtil: EnergyUtil):
        super(MeasureElectricityUsage, self).__init__(PROCESS_NAME, pid_dir=PID_DIR)
        self.energyUtil = energyUtil
        self.logger.addHandler(SysLogHandler(address=find_syslog(),
                                             facility=SysLogHandler.LOG_DAEMON))
        self.logger.setLevel(logging.DEBUG)
        self.logger.debug('initialized!')
    #     signal.signal(signal.SIGTERM, self.exit_gracefully)
    #
    # def exit_gracefully(self, signum, frame):
    #     self.logger.debug('>>>>>>>>>SOEMTHING KILLING')

    def run(self):
        self.create_save_measurement_jobs()


    def create_save_measurement_jobs(self):
        measure_jobname_base = "measuring_%s"

        self.logger.debug('Searching for measurement devices configured in the db')
        energy_devices = EnergyDeviceModel.get_all()
        self.logger.debug('Found %d measurement devices' % len(energy_devices))

        for energy_device in energy_devices:
            self.logger.debug('Found energy device %s, adding it to scheduler' % energy_device.energy_device_id)
            scheduler.add_job(id=measure_jobname_base % energy_device.energy_device_id,
                              func=save_measurement, args=[EnergyUtil(), energy_device.energy_device_id, self.logger],
                              trigger="interval", seconds=10)

        scheduler.start()


    def remove_measurement_jobs(self):
        self.logger.debug('>>>>>>>>>>>>>>>.stopping scheduled jobs')
        scheduler.remove_all_jobs()
        scheduler.shutdown()



def save_measurement(energy_util: EnergyUtil, energy_device_id, logger):
    logger.debug("starting measure %s" % energy_device_id)
    data = energy_util.getMeasurementValue(energy_device_id)
    device_measurement = EnergyDeviceMeasureModel(data)
    logger.debug('want to save %s %s %s' % (energy_device_id, device_measurement.id, device_measurement.created_at))
    device_measurement.save()
    logger.debug("value measured and saved %s %s %s" % (energy_device_id, device_measurement.id, device_measurement.created_at))


def main():
    logging.basicConfig(filename="/tmp/measurement_daemon.log")
    logging.basicConfig(level=logging.DEBUG)

    logger = logging.getLogger('measure_electricity_usage_daemon')

    env_name = os.getenv('CARCHARGING_ENV')

    logger.info('Starting for environment %s' % env_name)

    if len(sys.argv) != 2:
        sys.exit('Invalid COMMAND %s, give an argument, ie \'start\'' % sys.argv[0])

    cmd = sys.argv[1].lower()

    injector = Injector()
    service = injector.get(MeasureElectricityUsage)

    if cmd == 'start':
        service.start()
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
