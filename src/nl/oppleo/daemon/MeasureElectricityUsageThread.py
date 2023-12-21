import logging
import threading

from nl.oppleo.config.OppleoConfig import OppleoConfig
from nl.oppleo.models.EnergyDeviceMeasureModel import EnergyDeviceMeasureModel
from nl.oppleo.models.EnergyDeviceModel import EnergyDeviceModel
from nl.oppleo.daemon.EnergyDevice import EnergyDevice

oppleoConfig = OppleoConfig()

class MeasureElectricityUsageThread(object):
    appSocketIO = None
    threadLock = None
    stop_event = None

    def __init__(self, appSocketIO):
        self.logger = logging.getLogger('nl.oppleo.daemon.MeasureElectricityUsageThread')
        self.appSocketIO = appSocketIO
        self.thread = None
        self.stop_event = threading.Event()
        self.threadLock = threading.Lock()
        self.createEnergyDevice()

    def start(self):
        self.stop_event.clear()
        self.logger.debug('Launching background task...')
        self.logger.debug('start_background_task() - monitorEnergyDeviceLoop')
        # self.thread = self.appSocketIO.start_background_task(self.monitorEnergyDeviceLoop)
        #   appSocketIO.start_background_task launches a background_task
        #   This really doesn't do parallelism well, basically runs the whole thread befor it yields...
        #   Therefore use standard threads
        self.thread = threading.Thread(target=self.monitorEnergyDeviceLoop, name='kWhMeterReaderThread')
        self.thread.start()


    def stop(self):
        self.logger.debug('Requested to stop')
        self.stop_event.set()

    def createEnergyDevice(self):
        global oppleoConfig
        
        self.logger.info('Searching for measurement device configured in the db')
        energy_device_data = EnergyDeviceModel.get()
        if energy_device_data is None:
            self.logger.warn('No measurement device found!')
            return

        self.logger.info('Found energy device {} (enabled={}, simulate={})'.format(energy_device_data.energy_device_id, 
                                                                                   energy_device_data.device_enabled, 
                                                                                   energy_device_data.simulate))
        
        # Create energy device
        oppleoConfig.energyDevice = EnergyDevice(
                                        energy_device_id=energy_device_data.energy_device_id,
                                        modbusInterval=oppleoConfig.modbusInterval,
                                        enabled=energy_device_data.device_enabled,
                                        simulate=energy_device_data.simulate,
                                        appSocketIO=self.appSocketIO
                                        )

    def monitorEnergyDeviceLoop(self):
        global oppleoConfig
        self.logger.debug('monitorEnergyDeviceLoop()...')
        timer = 0
        while not self.stop_event.is_set():
            if (oppleoConfig.energyDevice is not None and 
                (oppleoConfig.energyDevice.enabled or oppleoConfig.energyDevice.simulate)
                ):
                oppleoConfig.energyDevice.handleIfTimeTo()
            # Sleep is interruptable by other threads, but sleeing 7 seconds before checking if 
            # stop is requested is a bit long, so sleep for 0.1 seconds, then check passed time
            self.appSocketIO.sleep(0.1)
            # Once every 5 seconds (50x 0.1s) check if None device can be instantiated, and if device is (still) enabled
            timer = timer +1 % 50
            if timer == 0:
                # Refresh
                energy_device_data = EnergyDeviceModel.get()
                if energy_device_data is not None and oppleoConfig.energyDevice is None:
                    self.createEnergyDevice()
                
        self.logger.debug(f'Terminating thread')


    # Callbacks called when new values are read
    def addCallback(self, fn):
        self.logger.debug('MeasureElectricityUsageThread.addCallback()...')
        if oppleoConfig.energyDevice is not None:
            self.logger.debug('MeasureElectricityUsageThread.addCallback() to energyDevice %s...' % oppleoConfig.energyDevice.energy_device_id)
            with self.threadLock:
                oppleoConfig.energyDevice.addCallback(fn)
        else:
            self.logger.debug('MeasureElectricityUsageThread.addCallback() FAILED - no energyDevice!')
            

