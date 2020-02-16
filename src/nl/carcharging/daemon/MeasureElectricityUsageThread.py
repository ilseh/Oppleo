import logging
import threading

from nl.carcharging.config.WebAppConfig import WebAppConfig
from nl.carcharging.models.EnergyDeviceMeasureModel import EnergyDeviceMeasureModel
from nl.carcharging.models.EnergyDeviceModel import EnergyDeviceModel
from nl.carcharging.utils.EnergyUtil import EnergyUtil
from nl.carcharging.daemon.EnergyDevice import EnergyDevice


class MeasureElectricityUsageThread(object):
    appSocketIO = None
    stop_event = None
    energyDevice = None

    def __init__(self, appSocketIO):
        self.logger = logging.getLogger('nl.carcharging.daemon.MeasureElectricityUsageThread')
        self.appSocketIO = appSocketIO
        self.thread = None
        self.stop_event = threading.Event()
        self.createEnergyDevicesList()

    def start(self):
        self.stop_event.clear()
        self.logger.debug('Launching background task...')
        self.logger.debug('start_background_task() - monitorEnergyDevicesLoop')
        self.thread = self.appSocketIO.start_background_task(self.monitorEnergyDevicesLoop)

    def stop(self):
        self.logger.debug('Requested to stop')
        self.stop_event.set()

    def createEnergyDevicesList(self):
        self.logger.info('Searching for measurement devices configured in the db')
        energy_device = EnergyDeviceModel.get()
        if energy_device is None:
            self.logger.warn('No measurement device found!')
        else:
            self.logger.info('Found energy device %s' % energy_device.energy_device_id)
            self.energyDevice = EnergyDevice(
                                    energy_device_id=energy_device.energy_device_id,
                                    modbusInterval=WebAppConfig.modbusInterval,
                                    energyUtil=EnergyUtil(
                                        energy_device_id=energy_device.energy_device_id,
                                        appSocketIO=self.appSocketIO
                                        ),
                                    appSocketIO=self.appSocketIO
                                    )

    def monitorEnergyDevicesLoop(self):
        global WebAppConfig
        self.logger.debug('monitorEnergyDevicesLoop()...')
        while not self.stop_event.is_set():
            if (self.energyDevice is not None):
                self.energyDevice.handleIfTimeTo()
            # Sleep is interruptable by other threads, but sleeing 7 seconds before checking if 
            # stop is requested is a bit long, so sleep for 0.1 seconds, then check passed time
            self.appSocketIO.sleep(0.1)
        self.logger.debug(f'Terminating thread')


    # Callbacks called when new values are read
    def addCallback(self, fn):
        self.logger.debug('MeasureElectricityUsageThread.addCallback()...')
        if self.energyDevice is not None:
            self.logger.debug('MeasureElectricityUsageThread.addCallback() to energyDevice %s...' % self.energyDevice.energy_device_id)
            self.energyDevice.addCallback(fn)


