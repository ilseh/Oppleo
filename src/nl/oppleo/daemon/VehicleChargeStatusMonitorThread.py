import threading
import logging
import time
import re

from nl.oppleo.config.OppleoConfig import OppleoConfig
from nl.oppleo.utils.WebSocketUtil import WebSocketUtil
from nl.oppleo.api.TeslaApi import TeslaAPI
from nl.oppleo.models.ChargeSessionModel import ChargeSessionModel
from nl.oppleo.models.RfidModel import RfidModel
from nl.oppleo.utils.UpdateOdometerTeslaUtil import UpdateOdometerTeslaUtil

oppleoConfig = OppleoConfig()

class VehicleChargeStatusMonitorThread(object):
    thread = None
    threadLock = None
    logger = None
    stop_event = None

    # Check every minute [60 seconds]
    vehicleMonitorInterval = 60

    sleepInterval = 0.25

    def __init__(self):
        self.threadLock = threading.Lock()
        self.stop_event = threading.Event()
        self.logger = logging.getLogger('nl.oppleo.daemon.VehicleChargeStatusMonitorThread')


    def toCamelcase(self, s):
        return re.sub(r'(?!^)_([a-zA-Z])', lambda m: m.group(1).upper(), s)


    def formatChargeStateParam(self, chargeState:dict=None, param:str=None):
        if chargeState is None or param is None:
            return chargeState
        try:
            return chargeState[param]
        except:
            return None

    def milesToKm(self, miles:float=0, acc:int=0):
        return round(miles * 1.609344 * pow(10, acc)) / pow(10, acc)


    """
        battery_level               battery percentage charged [int]
        battery_range               range in miles with current battery level [int]
        charge_energy_added         enery added in the charge session of the vehicle, in kWh [int]
        charge_limit_soc            charge limit percentage set [int]
        charge_limit_soc_max        max charge limit [int]
        charge_port_door_open       [True | False],
        charge_rate                 miles per hout [float]
        charger_actual_current      amps
        charger_phases              2 for three phases? [int]
        charger_power               in kW 
        charger_voltage             [Volts]
        charging_state              [Charging, Stopped, Complete, Disconnected]
        minutes_to_full_charge      70 [int] 
        time_to_full_charge         A value of 1.17 indicates 1.17 * 60min = 1u 10min = 70min [float]
        timestamp                   in millis
    """
    def formatChargeState(self, chargeState:dict=None):
        csEl = ['battery_level', 'battery_range', 'charge_energy_added', 'charge_limit_soc', 'charge_limit_soc_max', 
                'charge_miles_added_rated', 'charge_port_door_open', 'charge_port_latch', 'charge_rate', 'charger_actual_current', 'charger_phases',
                'charger_power', 'charger_voltage', 'charging_state', 'minutes_to_full_charge', 'time_to_full_charge', 
                'timestamp']
        # Which ones are in miles
        csElMiles = ['charge_miles_added_rated', 'charge_rate']
        csElKm = ['charge_km_added_rated', 'charge_rate']
        if chargeState is None:
            return {}

        csDict = {}
        for el in csEl:
            csDict[self.toCamelcase(el)] = self.formatChargeStateParam(chargeState, el)
            if el in csElMiles:
                # Convert
                csDict[self.toCamelcase(csElKm[csElMiles.index(el)])] = self.milesToKm(csDict[self.toCamelcase(el)], 1)
                if el != csElKm[csElMiles.index(el)]:
                    # Only delete if it was stored on a different key
                    del csDict[self.toCamelcase(el)]

        return csDict



    # VehicleChargeStatusMonitorThread
    def monitor(self):
        """
            if open charge session and vehicle information, send updates
        """
        teslaApi = TeslaAPI()

        while not self.stop_event.is_set():
            openSession = ChargeSessionModel.getOpenChargeSession(oppleoConfig.chargerName)
            if openSession is not None:
                # skip
                rfidTag = RfidModel().get_one(openSession.rfid)
                if rfidTag != None:
                    UpdateOdometerTeslaUtil.copy_token_from_rfid_model_to_api(rfidTag, teslaApi)
                    if teslaApi.hasValidToken():
                        # Refresh if required (check once per day)
                        if teslaApi.refreshTokenIfRequired():
                            UpdateOdometerTeslaUtil.copy_token_from_api_to_rfid_model(teslaApi, rfidTag)
                            rfidTag.save()

                        chargeState = teslaApi.getChargeStateWithId(rfidTag.vehicle_id)

                        # Send change notification
                        WebSocketUtil.emit(
                                wsEmitQueue=oppleoConfig.wsEmitQueue,
                                event='vehicle_status_update', 
                                id=oppleoConfig.chargerName,
                                data=self.formatChargeState(chargeState),
                                namespace='/charge_session',
                                public=True
                                )

            # Sleep for quite a while, and yield for other threads
            time.sleep(self.sleepInterval)

        self.logger.info("Stopping VehicleChargeStatusMonitorThread")


    def start(self):
        self.stop_event.clear()
        self.logger.debug('Launching Thread...')

        self.thread = threading.Thread(target=self.monitor, name='VehicleChargeStatusMonitorThread')
        self.thread.start()

    def stop(self, block=False):
        self.logger.debug('Requested to stop')
        self.stop_event.set()
