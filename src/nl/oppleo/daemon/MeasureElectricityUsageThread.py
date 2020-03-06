import logging
import threading

from nl.oppleo.config.OppleoConfig import OppleoConfig
from nl.oppleo.models.EnergyDeviceMeasureModel import EnergyDeviceMeasureModel
from nl.oppleo.models.EnergyDeviceModel import EnergyDeviceModel
from nl.oppleo.utils.EnergyUtil import EnergyUtil
from nl.oppleo.daemon.EnergyDevice import EnergyDevice


class MeasureElectricityUsageThread(object):
    appSocketIO = None
    stop_event = None
    energyDevice = None

    def __init__(self, appSocketIO):
        self.logger = logging.getLogger('nl.oppleo.daemon.MeasureElectricityUsageThread')
        self.appSocketIO = appSocketIO
        self.thread = None
        self.stop_event = threading.Event()
        self.createEnergyDevicesList()

    def start(self):
        self.stop_event.clear()
        self.logger.debug('Launching background task...')
        self.logger.debug('start_background_task() - monitorEnergyDevicesLoop')
        # self.thread = self.appSocketIO.start_background_task(self.monitorEnergyDevicesLoop)
        #   appSocketIO.start_background_task launches a background_task
        #   This really doesn't do parallelism well, basically runs the whole thread befor it yields...
        #   Therefore use standard threads
        self.thread = threading.Thread(target=self.monitorEnergyDevicesLoop, name='KwhMeterReaderThread')
        self.thread.start()


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
                                    modbusInterval=OppleoConfig.modbusInterval,
                                    energyUtil=EnergyUtil(
                                        energy_device_id=energy_device.energy_device_id,
                                        appSocketIO=self.appSocketIO
                                        ),
                                    appSocketIO=self.appSocketIO
                                    )

    def monitorEnergyDevicesLoop(self):
        global OppleoConfig
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


