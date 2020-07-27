
from configparser import RawConfigParser, NoSectionError, NoOptionError, ExtendedInterpolation
import logging
from datetime import datetime
import os
from nl.oppleo.models.ChargerConfigModel import ChargerConfigModel
from nl.oppleo.models.EnergyDeviceModel import EnergyDeviceModel
from nl.oppleo.config import Logger
from nl.oppleo.utils.WebSocketUtil import WebSocketUtil

"""
 Instantiate an OppleoConfig() object. This will be a Singleton
 
"""

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


# 
class OppleoConfig(object, metaclass=Singleton):

    """
        Variables not stored in the database (hardcoded) 
    """

    # ENERGY_DEVICE_ID = 'NONE'
    # PYTHONPATH = ''
    # EXPLAIN_TEMPLATE_LOADING = False

    # INI params
    # PRODUCTION = False
    # DEBUG = True
    # TESTING = False

    # httpHost = '0.0.0.0'  
    # httpPort = 80
    # useReloader = False
    # Factor to calculate km/h equivalent of Wh per km
    # Tesla is using 162, which matches the in-car screen
    # Actual average over first 16.836 km on Tesla Model 3 is 181.8
    # factor_Whkm = 162

    # Number of seconds between consecutive kwh meter readouts (via modbus). Only changes will be stored in the 
    # usage table. Greater values will lead to lagging change detection. Smaller values take more processing.
    # modbusInterval = 10

    # Auto Session starts a new session when the EVSE starts charging and during the set amount of minutes less
    # than the amount of energy has been consumed (auto was away)
    # A Tesla Model 3 75kWh Dual Motor charges 0.2kWh every 1:23h (16 feb 2020)
    # autoSessionEnabled = False
    # autoSessionMinutes = 90
    # autoSessionEnergy = 0.1
    # Condenses autyo-generated sessions (after a period of inactivity) if the odometer has not changed.
    # Auto-sessions can be generated after the charger was switched off in peak period. Start of off-peak then leads to 
    # an incorrectly auto-generated charge-session, while the vehicke actually has not moved.
    # This does not condense sessions stopped and started through RFID or WebApp.
    # autoSessionCondenseSameOdometer = False

    # GPIO MODE - BCM or BOARD (BCM is more future proof/ less direct hardware related)
    #   -1 if GPIO.setmode() is not set
    #   11 if GPIO.setmode(GPIO.BCM) is active
    #   10 if GPIO.setmode(GPIO.BOARD) is active
    # Once you’ve set the mode, you can only change it once you’ve done a GPIO.cleanup(). But you can only do 
    # GPIO.cleanup() once you’ve configured a port. You can’t flick between GPIO modes without first setting up 
    # a port, then cleaning up.
    # gpioMode = 'BCM'
    # Pulsing LED values
    # pulseLedMin = 3
    # pulseLedMax = 98
    # Raspberry PINs - RGB LEDs - PINS GPIO13 (Red), GPIO12 (Green) and GPIO 16 (Blue)
    # pinLedRed = 13
    # pinLedGreen = 12
    # pinLedBlue = 16
    # Raspberry PINs - Buzzer - PIN 16/ GPIO23
    # pinBuzzer = 23 
    # Raspberry PINs - Buzzer - PIN 29/ GPIO5
    # pinEvseSwitch = 5
    # Raspberry PINs - Buzzer - PIN 31/ GPIO6
    # pinEvseLed = 6

    # Peak/ Off Peak enabled. If enabled the EVSE will be disabled during off-peak hours
    # peakHoursOffPeakEnabled = True
    # Off Peak disabled for this period (not-persistent)
    # peakHoursAllowPeakOnePeriod = False


    """
        Private variables
    """
    # OppleoConfig Logger
    ___logger = None
    __chargerConfigModel = None
    __restartRequired = False
    __upSinceDatetime = datetime.now()


    """
        Global location to store all connected clients keyed by request.sid (websocket room)
    """
    connectedClients = {}

    """
        Application wide global variables or handles which can be picked op from here
    """
    login_manager = None
    # Flask app and socketio app
    app = None  
    appSocketIO = None

    meuThread = None
    chThread = None
    phmThread = None

    wsEmitQueue = None

    """
        Global location to store kWh meter serial number
    """
    kWhMeter_serial = None


    def __init__(self):
        self.___logger = logging.getLogger('nl.oppleo.config.' + self.__class__.__name__)
        self.___logger.debug('Initializing Oppleo...')
        self.__chargerConfigModel = ChargerConfigModel.get_config()


    """
        chargerName --> charger_name
    """
    @property
    def chargerName(self):
        return self.__chargerConfigModel.charger_name

    @chargerName.setter
    def chargerName(self, value):
        self.__chargerConfigModel.setAndSave('charger_name', value)
        energyDeviceModel = EnergyDeviceModel.get()
        energyDeviceModel.energy_device_id = value
        energyDeviceModel.save()
        self.restartRequired = True

    """
        chargerTariff --> charger_tariff
    """
    @property
    def chargerTariff(self):
        return self.__chargerConfigModel.charger_tariff

    @chargerTariff.setter
    def chargerTariff(self, value):
        self.__chargerConfigModel.setAndSave('charger_tariff', value)

    """
        modifiedAt --> modified_at
    """
    @property
    def modifiedAt(self):
        return self.__chargerConfigModel.modified_at

    # In principle the modified_at is updated by ChargerConfigModel on saves
    @modifiedAt.setter
    def modifiedAt(self, value):
        self.__chargerConfigModel.setAndSave('modified_at', value)

    def generateNewSecretKeys(self):
        self.secretKey = os.urandom(24)
        self.csrfSecretKey = os.urandom(24)
        self.restartRequired = True

    """
        secretKey --> secret_key
    """
    @property
    def secretKey(self):
        return self.__chargerConfigModel.secret_key

    @secretKey.setter
    def secretKey(self, value):
        self.__chargerConfigModel.setAndSave('secret_key', value)
        self.restartRequired = True

    """
        csrfSecretKey --> wtf_csrf_secret_key
    """
    @property
    def csrfSecretKey(self):
        return self.__chargerConfigModel.wtf_csrf_secret_key

    @csrfSecretKey.setter
    def csrfSecretKey(self, value):
        self.__chargerConfigModel.setAndSave('wtf_csrf_secret_key', value)
        self.restartRequired = True

    """
        httpHost --> http_host
    """
    @property
    def httpHost(self):
        return self.__chargerConfigModel.http_host

    @httpHost.setter
    def httpHost(self, value):
        self.__chargerConfigModel.setAndSave('http_host', value)
        self.restartRequired = True

    """
        httpPort --> http_port
    """
    @property
    def httpPort(self):
        return self.__chargerConfigModel.http_port

    @httpPort.setter
    def httpPort(self, value):
        self.__chargerConfigModel.setAndSave('http_port', value)
        self.restartRequired = True


    """
        useReloader --> use_reloader
    """
    @property
    def useReloader(self):
        return self.__chargerConfigModel.use_reloader

    @useReloader.setter
    def useReloader(self, value):
        self.__chargerConfigModel.setAndSave('use_reloader', value)
        self.restartRequired = True

    """
        factorWhkm --> factor_whkm
    """
    @property
    def factorWhkm(self):
        return self.__chargerConfigModel.factor_whkm

    @factorWhkm.setter
    def factorWhkm(self, value):
        self.__chargerConfigModel.setAndSave('factor_whkm', value)

    """
        modbusInterval --> modbus_interval
    """
    @property
    def modbusInterval(self):
        return self.__chargerConfigModel.modbus_interval

    @modbusInterval.setter
    def modbusInterval(self, value):
        self.__chargerConfigModel.setAndSave('modbus_interval', value)
        self.restartRequired = True

    """
        autoSessionEnabled --> autosession_enabled
    """
    @property
    def autoSessionEnabled(self):
        return self.__chargerConfigModel.autosession_enabled

    @autoSessionEnabled.setter
    def autoSessionEnabled(self, value):
        self.__chargerConfigModel.setAndSave('autosession_enabled', value)

    """
        autoSessionMinutes --> autosession_minutes
    """
    @property
    def autoSessionMinutes(self):
        return self.__chargerConfigModel.autosession_minutes

    @autoSessionMinutes.setter
    def autoSessionMinutes(self, value):
        self.__chargerConfigModel.setAndSave('autosession_minutes', value)

    """
        autoSessionEnergy --> autosession_energy
    """
    @property
    def autoSessionEnergy(self):
        return self.__chargerConfigModel.autosession_energy

    @autoSessionEnergy.setter
    def autoSessionEnergy(self, value):
        self.__chargerConfigModel.setAndSave('autosession_energy', value)

    """
        autoSessionCondenseSameOdometer --> autosession_condense_same_odometer
    """
    @property
    def autoSessionCondenseSameOdometer(self):
        return self.__chargerConfigModel.autosession_condense_same_odometer

    @autoSessionCondenseSameOdometer.setter
    def autoSessionCondenseSameOdometer(self, value):
        self.__chargerConfigModel.setAndSave('autosession_condense_same_odometer', value)

    """
        pulseLedMin --> pulseled_min
    """
    @property
    def pulseLedMin(self):
        return self.__chargerConfigModel.pulseled_min

    @pulseLedMin.setter
    def pulseLedMin(self, value):
        self.__chargerConfigModel.setAndSave('pulseled_min', value)
        self.restartRequired = True

    """
        pulseLedMax --> pulseled_max
    """
    @property
    def pulseLedMax(self):
        return self.__chargerConfigModel.pulseled_max

    @pulseLedMax.setter
    def pulseLedMax(self, value):
        self.__chargerConfigModel.setAndSave('pulseled_max', value)
        self.restartRequired = True

    """
        gpioMode --> gpio_mode
    """
    @property
    def gpioMode(self):
        return self.__chargerConfigModel.gpio_mode

    @gpioMode.setter
    def gpioMode(self, value):
        self.__chargerConfigModel.setAndSave('gpio_mode', value, ['BCM', 'BOARD'])
        self.restartRequired = True

    """
        pinLedRed --> pin_led_red
    """
    @property
    def pinLedRed(self):
        return self.__chargerConfigModel.pin_led_red

    @pinLedRed.setter
    def pinLedRed(self, value):
        self.__chargerConfigModel.setAndSave('pin_led_red', value)
        self.restartRequired = True

    """
        pinLedGreen --> pin_led_green
    """
    @property
    def pinLedGreen(self):
        return self.__chargerConfigModel.pin_led_green

    @pinLedGreen.setter
    def pinLedGreen(self, value):
        self.__chargerConfigModel.setAndSave('pin_led_green', value)
        self.restartRequired = True

    """
        pinLedBlue --> pin_led_blue
    """
    @property
    def pinLedBlue(self):
        return self.__chargerConfigModel.pin_led_blue

    @pinLedBlue.setter
    def pinLedBlue(self, value):
        self.__chargerConfigModel.setAndSave('pin_led_blue', value)
        self.restartRequired = True

    """
        pinBuzzer --> pin_buzzer
    """
    @property
    def pinBuzzer(self):
        return self.__chargerConfigModel.pin_buzzer

    @pinBuzzer.setter
    def pinBuzzer(self, value):
        self.__chargerConfigModel.setAndSave('pin_buzzer', value)
        self.restartRequired = True


    """
        pinEvseSwitch --> pin_evse_switch
    """
    @property
    def pinEvseSwitch(self):
        return self.__chargerConfigModel.pin_evse_switch

    @pinEvseSwitch.setter
    def pinEvseSwitch(self, value):
        self.__chargerConfigModel.setAndSave('pin_evse_switch', value)
        self.restartRequired = True

    """
        pinEvseLed --> pin_evse_led
    """
    @property
    def pinEvseLed(self):
        return self.__chargerConfigModel.pin_evse_led

    @pinEvseLed.setter
    def pinEvseLed(self, value):
        self.__chargerConfigModel.setAndSave('pin_evse_led', value)
        self.restartRequired = True


    """
        offpeakEnabled --> peakhours_offpeak_enabled
    """
    @property
    def offpeakEnabled(self):
        return self.__chargerConfigModel.peakhours_offpeak_enabled

    @offpeakEnabled.setter
    def offpeakEnabled(self, value):
        self.__chargerConfigModel.setAndSave('peakhours_offpeak_enabled', value)

    """
        allowPeakOnePeriod --> peakhours_allow_peak_one_period
    """
    @property
    def allowPeakOnePeriod(self):
        return self.__chargerConfigModel.peakhours_allow_peak_one_period

    @allowPeakOnePeriod.setter
    def allowPeakOnePeriod(self, value):
        self.__chargerConfigModel.setAndSave('peakhours_allow_peak_one_period', value)

    """
        prowlEnabled --> prowl_enabled
    """
    @property
    def prowlEnabled(self):
        return self.__chargerConfigModel.prowl_enabled

    @prowlEnabled.setter
    def prowlEnabled(self, value):
        self.__chargerConfigModel.setAndSave('prowl_enabled', value)

    """
        prowlApiKey --> prowl_apikey
    """
    @property
    def prowlApiKey(self):
        return self.__chargerConfigModel.prowl_apikey

    @prowlApiKey.setter
    def prowlApiKey(self, value):
        self.__chargerConfigModel.setAndSave('prowl_apikey', value)

    """
        logFile --> log_file
    """
    @property
    def logFile(self):
        return self.__chargerConfigModel.log_file

    @logFile.setter
    def logFile(self, value):
        self.__chargerConfigModel.setAndSave('log_file', value)
        self.restartRequired = True


    """
        restartRequired (no database persistence)
    """
    @property
    def restartRequired(self):
        return self.__restartRequired

    @restartRequired.setter
    def restartRequired(self, value):
        try: 
            self.__restartRequired = bool(value)
            if (bool(value)):
                # Announce
                WebSocketUtil.emit(
                        wsEmitQueue=self.wsEmitQueue,
                        event='update', 
                        id=self.chargerName,
                        data={
                            "restartRequired"   : self.__restartRequired,
                            "upSince"           : self.upSinceDatetimeStr,
                            "clientsConnected"  : len(self.connectedClients)
                        },
                        namespace='/system_status/',
                        public=False
                    )

        except ValueError:
            self.___logger.warning("Value {} could not be interpreted as bool".format(value), exc_info=True)

    """
        upSinceDatetime (set on startup, no setter)
    """
    @property
    def upSinceDatetime(self):
        return self.__upSinceDatetime

    @upSinceDatetime.setter
    def upSinceDatetime(self, value):
        raise NotImplementedError('upSinceDatetime set at boot.')

    @property
    def upSinceDatetimeStr(self):
        return self.__upSinceDatetime.strftime("%d/%m/%Y, %H:%M:%S")

    @upSinceDatetimeStr.setter
    def upSinceDatetimeStr(self, value):
        raise NotImplementedError('upSinceDatetime set at boot.')


    """
        webChargeOnDashboard --> webcharge_on_dashboard
    """
    @property
    def webChargeOnDashboard(self):
        return self.__chargerConfigModel.webcharge_on_dashboard

    @webChargeOnDashboard.setter
    def webChargeOnDashboard(self, value):
        self.__chargerConfigModel.setAndSave('webcharge_on_dashboard', value)

    """
        authWebCharge --> auth_webcharge
    """
    @property
    def authWebCharge(self):
        return self.__chargerConfigModel.auth_webcharge

    @authWebCharge.setter
    def authWebCharge(self, value):
        self.__chargerConfigModel.setAndSave('auth_webcharge', value)


