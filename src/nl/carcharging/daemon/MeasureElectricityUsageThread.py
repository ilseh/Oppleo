import logging
import threading

from nl.carcharging.models.EnergyDeviceMeasureModel import EnergyDeviceMeasureModel
from nl.carcharging.models.EnergyDeviceModel import EnergyDeviceModel
from nl.carcharging.utils.EnergyUtil import EnergyUtil
from nl.carcharging.daemon.EnergyDevice import EnergyDevice


class MeasureElectricityUsageThread(object):
    appSocketIO = None
    stop_event = None
    energyDeviceList = []


    def __init__(self):
        self.logger = logging.getLogger('nl.carcharging.daemon.MeasureElectricityUsageThread')
        self.thread = None
        self.stop_event = threading.Event()

    def start(self, appSocketIO):
        self.stop_event.clear()
        self.logger.debug('Launching background task...')
        self.appSocketIO = appSocketIO
        self.logger.debug('start_background_task() - monitorEnergyDevicesLoop')
        self.thread = self.appSocketIO.start_background_task(self.monitorEnergyDevicesLoop)

    def stop(self):
        self.logger.debug('Requested to stop')
        self.stop_event.set()

    def createEnergyDevicesList(self):
        self.logger.info('Searching for measurement devices configured in the db')
        energy_devices = EnergyDeviceModel.get_all()
        self.logger.info('Found %d measurement devices' % len(energy_devices))

        for energy_device in energy_devices:
            self.logger.info('Found energy device %s, adding it to monitoring list' % energy_device.energy_device_id)
            self.energyDeviceList.append(
                EnergyDevice(
                    energy_device_id=energy_device.energy_device_id,
                    interval=10,
                    energyUtil=EnergyUtil(),
                    appSocketIO=self.appSocketIO
                    )
                )
        # Continue looping through them

    def monitorEnergyDevicesLoop(self):
        global WebAppConfig
        self.logger.debug('monitorEnergyDevicesLoop()...')
        self.createEnergyDevicesList()
        while not self.stop_event.is_set():
            for energyDevice in self.energyDeviceList:
                # Sleep is interruptable by other threads, but sleeing 7 seconds before checking if 
                # stop is requested is a bit long, so sleep for 0.1 seconds, then check passed time
                energyDevice.handleIfTimeTo()
            self.appSocketIO.sleep(0.1)
        self.logger.debug(f'Terminating thread')


    # Callbacks called when new values are read
    def addCallback(self, fn):
        for energyDevice in self.energyDeviceList:
            energyDevice.addCallback(fn)


