
from configparser import RawConfigParser, NoSectionError, NoOptionError, ExtendedInterpolation
import logging
from datetime import datetime
import os
import json
from json import JSONDecodeError

from nl.oppleo.models.ChargerConfigModel import ChargerConfigModel
from nl.oppleo.models.EnergyDeviceModel import EnergyDeviceModel
from nl.oppleo.models.ChargeSessionModel import ChargeSessionModel
from nl.oppleo.config import Logger
from nl.oppleo.utils.IPv4 import IPv4

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
    # Once you’ve set the mode, you can only change it after a GPIO.cleanup(). You can only GPIO.cleanup() 
    # after configuring at least one port. You can’t flick between GPIO modes without first setting up a port.
    # GPIO.cleanup() also resets SPI ports, disabling the SPI untill reboot.
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

    BACKUP_INTERVAL_WEEKDAY = "w"
    BACKUP_INTERVAL_CALDAY  = "c"

    """ 
        Offsite Backup type. For now only Samba (Windows shared drive) supported. Future expansions to AFP, OneDrive, iCloud Drive etc.
    """
    OS_BACKUP_TYPE_UNKNOWN      = '-'
    OS_BACKUP_TYPE_SMB          = 'smb'
    OS_BACKUP_TYPE_SMB_STR      = 'Server Message Block (SMB)'
    OS_BACKUP_TYPE_AFP          = 'afp'
    OS_BACKUP_TYPE_AFP_STR      = 'Apple Filing Protocol (AFP)'
    OS_BACKUP_TYPE_ONEDRIVE     = 'onedrive'
    OS_BACKUP_TYPE_ONEDRIVE_STR = 'Microsoft OneDrive'
    OS_BACKUP_TYPE_ICLOUD       = 'icloud'
    OS_BACKUP_TYPE_ICLOUD_STR   = 'Apple iCloud'
    
    BACKUP_DIR_NAME             = 'backup'
    DOC_DIR_NAME                = 'doc'

    
    """
        Private variables
    """
    # OppleoConfig Logger
    __logger = None
    __chargerConfigModel = None
    __restartRequired = False
    __upSinceDatetime = datetime.now()
    __softwareUpdateInProgress = False


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

    meuThread = None        # MeasureElectricityUsageThread
    chThread = None         # ChargerHandlerThread
    phmThread = None        # PeakHoursMonitorThread
    rgblcThread = None      # RGBLedControllerThread
    vcsmThread = None       # VehicleChargeStatusMonitorThread
    vuThread = None         # VehicleUtilThread (TeslaUtilThread) - background task, a.o. capture odometer
    mqttshThread = None     # MqttSendHistoryThread
    
    wsEmitQueue = None

    energyDevice = None
    
    """
        Global location to store kWh meter serial number
    """
    kWhMeter_serial = None

    def __init__(self):
        self.__logger = logging.getLogger(__name__)
        self.__logger.debug('Initializing Oppleo...')
        self.__chargerConfigModel = ChargerConfigModel.get_config()

    """
        chargerID --> charger_id
    """
    @property
    def chargerID(self):
        return self.__chargerConfigModel.charger_id

    @chargerID.setter
    def chargerID(self, value):
        oldChargerId = self.chargerID

        # First create new energy device config (duplicate old)
        energyDeviceModel = EnergyDeviceModel.get(energy_device_id=oldChargerId)
        newEnergyDeviceModel = energyDeviceModel.duplicate(newEnergyDeviceId=value)

        # Migrate all charge sessions to the new ID
        ChargeSessionModel.migrateEnergyDevice(fromEnergyDeviceId=oldChargerId, toEnergyDeviceId=value)

        # Update config
        self.__chargerConfigModel.setAndSave('charger_id', value)

        # Delete the old energyDeviceModel
        oldEnergyDeviceModel = EnergyDeviceModel.get(energy_device_id=oldChargerId)
        oldEnergyDeviceModel.delete()

        # Indicate restart required (the ID is used in websocket communications)
        self.restartRequired = True

    """
        chargerNameText --> charger_name_text
    """
    @property
    def chargerNameText(self):
        return self.__chargerConfigModel.charger_name_text

    @chargerNameText.setter
    def chargerNameText(self, value):
        self.__chargerConfigModel.setAndSave('charger_name_text', value)

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
        kWhMeterSerial --> kWhMeter_serial
    """
    @property
    def kWhMeterSerial(self):
        return self.kWhMeter_serial

    @kWhMeterSerial.setter
    def kWhMeterSerial(self, value):
        self.kWhMeter_serial = value


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
                # Import here to prevent instantiation when OppleoSystemConfig is instantiated
                from nl.oppleo.utils.OutboundEvent import OutboundEvent 
                # Announce
                OutboundEvent.triggerEvent(
                        event='update', 
                        id=self.chargerID,
                        data={
                            "restartRequired"           : self.__restartRequired,
                            'softwareUpdateInProgress'  : self.__softwareUpdateInProgress,
                            "upSince"                   : self.upSinceDatetimeStr,
                            "clientsConnected"          : len(self.connectedClients)
                        },
                        namespace='/system_status',
                        public=False
                    )

        except ValueError:
            self.__logger.warning("@restartRequired.setter - Value {} could not be interpreted as bool".format(value), exc_info=True)


    """
        softwareUpdateInProgress (no database persistence)
    """
    @property
    def softwareUpdateInProgress(self):
        return self.__softwareUpdateInProgress

    @softwareUpdateInProgress.setter
    def softwareUpdateInProgress(self, value):
        try: 
            self.__softwareUpdateInProgress = bool(value)
            if (bool(value)):
                # Import here to prevent instantiation when OppleoSystemConfig is instantiated
                from nl.oppleo.utils.OutboundEvent import OutboundEvent 
                # Announce
                OutboundEvent.triggerEvent(
                        event='update', 
                        id=self.chargerID,
                        data={
                            "restartRequired"           : self.__restartRequired,
                            'softwareUpdateInProgress'  : self.__softwareUpdateInProgress,
                            "upSince"                   : self.upSinceDatetimeStr,
                            "clientsConnected"          : len(self.connectedClients)
                        },
                        namespace='/system_status',
                        public=False
                    )

        except ValueError:
            self.__logger.warning("@softwareUpdateInProgress.setter - Value {} could not be interpreted as bool".format(value), exc_info=True)



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
        wakeupVehicleOnDataRequest --> wakeup_vehicle_on_data_request
    """
    @property
    def wakeupVehicleOnDataRequest(self):
        return self.__chargerConfigModel.wakeup_vehicle_on_data_request

    @wakeupVehicleOnDataRequest.setter
    def wakeupVehicleOnDataRequest(self, value):
        self.__chargerConfigModel.setAndSave('wakeup_vehicle_on_data_request', value)

    """
        authWebCharge --> auth_webcharge
    """
    @property
    def authWebCharge(self):
        return self.__chargerConfigModel.auth_webcharge

    @authWebCharge.setter
    def authWebCharge(self, value):
        self.__chargerConfigModel.setAndSave('auth_webcharge', value)

    """
        restrictDashboardAccess --> restrict_dashboard_access
    """
    @property
    def restrictDashboardAccess(self):
        return self.__chargerConfigModel.restrict_dashboard_access

    @restrictDashboardAccess.setter
    def restrictDashboardAccess(self, value):
        self.__chargerConfigModel.setAndSave('restrict_dashboard_access', value)

    """
        restrictMenu --> restrict_menu
    """
    @property
    def restrictMenu(self):
        return self.__chargerConfigModel.restrict_menu

    @restrictMenu.setter
    def restrictMenu(self, value):
        self.__chargerConfigModel.setAndSave('restrict_menu', value)

    """
        allowLocalDashboardAccess --> allow_local_dashboard_access
    """
    @property
    def allowLocalDashboardAccess(self):
        return self.__chargerConfigModel.allow_local_dashboard_access

    @allowLocalDashboardAccess.setter
    def allowLocalDashboardAccess(self, value):
        self.__chargerConfigModel.setAndSave('allow_local_dashboard_access', value)

    """
        routerIPAddress --> router_ip_address
        Return list of ip strings, with /b bitmask
        Backward compatible with single IP-address string in database
    """
    @property
    def routerIPAddress(self):
        # Old: string with one IP, new: json with ip and mask
        try:
            return json.loads(self.__chargerConfigModel.router_ip_address)
        except JSONDecodeError as jde:
            # Not json, old string, convert
            pass
        newList = []
        oldValue = self.__chargerConfigModel.router_ip_address

        # Convert to subnet
        newList.append( oldValue + '/32' if ( IPv4.validIP(oldValue) and not IPv4.validSubnet(oldValue)) else '' )
        # Store the list
        self.routerIPAddress = newList

        return newList

    @routerIPAddress.setter
    def routerIPAddress(self, ip_list:list=None):
        if ip_list is None: 
            ip_list = []
        for i in range(len(ip_list)):            
            if IPv4.validIP(ip_list[i]) and not IPv4.validSubnet(ip_list[i]):
                ip_list[i] = ip_list[i] + '/32'
        self.__chargerConfigModel.setAndSave('router_ip_address', json.dumps(ip_list, default=str))

    """
        receiptPrefix --> receipt_prefix
    """
    @property
    def receiptPrefix(self):
        return self.__chargerConfigModel.receipt_prefix

    @receiptPrefix.setter
    def receiptPrefix(self, value):
        self.__chargerConfigModel.setAndSave('receipt_prefix', value)


    """
        backupEnabled --> backup_enabled
    """
    @property
    def backupEnabled(self):
        return self.__chargerConfigModel.backup_enabled

    @backupEnabled.setter
    def backupEnabled(self, value):
        self.__chargerConfigModel.setAndSave('backup_enabled', value)

    """
        backupInterval --> backup_interval
    """
    @property
    def backupInterval(self):
        return self.__chargerConfigModel.backup_interval

    @backupInterval.setter
    def backupInterval(self, value):
        self.__chargerConfigModel.setAndSave('backup_interval', value)

    """
        backupIntervalWeekday --> backup_interval_weekday
    """
    @property
    def backupIntervalWeekday(self):
        return self.__chargerConfigModel.backup_interval_weekday

    @backupIntervalWeekday.setter
    def backupIntervalWeekday(self, value):
        self.__chargerConfigModel.setAndSave('backup_interval_weekday', value)

    """
        backupIntervalCalday --> backup_interval_calday
    """
    @property
    def backupIntervalCalday(self):
        return self.__chargerConfigModel.backup_interval_calday

    @backupIntervalCalday.setter
    def backupIntervalCalday(self, value):
        self.__chargerConfigModel.setAndSave('backup_interval_calday', value)

    """
        backupTimeOfDay --> backup_time_of_day
    """
    @property
    def backupTimeOfDay(self):
        return self.__chargerConfigModel.backup_time_of_day

    @backupTimeOfDay.setter
    def backupTimeOfDay(self, value):
        self.__chargerConfigModel.setAndSave('backup_time_of_day', value)

    """
        backupSuccessTimestamp --> backup_success_timestamp
    """
    @property
    def backupSuccessTimestamp(self):
        return self.__chargerConfigModel.backup_success_timestamp

    @backupSuccessTimestamp.setter
    def backupSuccessTimestamp(self, value):
        self.__chargerConfigModel.setAndSave('backup_success_timestamp', value)

    """
        returns the absolute path to the Oppleo root folder
    """
    @property
    def oppleoRootDirectory(self) -> str:
        return os.path.dirname(os.path.realpath(__file__)).split('src/nl/oppleo/config')[0]
        # return os.path.realpath(".")


    """
        returns the absolute path to the backup folder
    """
    @property
    def localBackupDirectory(self) -> str:
        return os.path.join(self.oppleoRootDirectory, self.BACKUP_DIR_NAME)

    """
        backupLocalHistory --> backup_local_history
    """
    @property
    def backupLocalHistory(self):
        return self.__chargerConfigModel.backup_local_history

    @backupLocalHistory.setter
    def backupLocalHistory(self, value):
        self.__chargerConfigModel.setAndSave('backup_local_history', value)

    """
        osBackupEnabled --> os_backup_enabled
    """
    @property
    def osBackupEnabled(self):
        return self.__chargerConfigModel.os_backup_enabled

    @osBackupEnabled.setter
    def osBackupEnabled(self, value):
        self.__chargerConfigModel.setAndSave('os_backup_enabled', value)

    """
        osBackupType --> os_backup_type
    """
    @property
    def osBackupType(self):
        return self.__chargerConfigModel.os_backup_type

    @osBackupType.setter
    def osBackupType(self, value):
        self.__chargerConfigModel.setAndSave('os_backup_type', value)

    """
        osBackupHistory --> os_backup_history
    """
    @property
    def osBackupHistory(self):
        return self.__chargerConfigModel.os_backup_history

    @osBackupHistory.setter
    def osBackupHistory(self, value):
        self.__chargerConfigModel.setAndSave('os_backup_history', value)

    """
        smbBackupServerNameOrIPAddress --> smb_backup_servername_or_ip_address
    """
    @property
    def smbBackupServerNameOrIPAddress(self):
        return self.__chargerConfigModel.smb_backup_servername_or_ip_address

    @smbBackupServerNameOrIPAddress.setter
    def smbBackupServerNameOrIPAddress(self, value):
        self.__chargerConfigModel.setAndSave('smb_backup_servername_or_ip_address', value)

    """
        smbBackupUsername --> smb_backup_username
    """
    @property
    def smbBackupUsername(self):
        return self.__chargerConfigModel.smb_backup_username

    @smbBackupUsername.setter
    def smbBackupUsername(self, value):
        self.__chargerConfigModel.setAndSave('smb_backup_username', value)

    """
        smbBackupPassword --> smb_backup_password
    """
    @property
    def smbBackupPassword(self):
        return self.__chargerConfigModel.smb_backup_password

    @smbBackupPassword.setter
    def smbBackupPassword(self, value):
        self.__chargerConfigModel.setAndSave('smb_backup_password', value)

    """
        smbBackupServiceName --> smb_backup_service_name
    """
    @property
    def smbBackupServiceName(self):
        return self.__chargerConfigModel.smb_backup_service_name

    @smbBackupServiceName.setter
    def smbBackupServiceName(self, value):
        self.__chargerConfigModel.setAndSave('smb_backup_service_name', value)

    """
        smbBackupRemotePath --> smb_backup_remote_path
    """
    @property
    def smbBackupRemotePath(self):
        return self.__chargerConfigModel.smb_backup_remote_path

    @smbBackupRemotePath.setter
    def smbBackupRemotePath(self, value):
        self.__chargerConfigModel.setAndSave('smb_backup_remote_path', value)


    """
        vehicleDataOnDashboard --> vehicle_data_on_dashboard
    """
    @property
    def vehicleDataOnDashboard(self):
        return self.__chargerConfigModel.vehicle_data_on_dashboard

    @vehicleDataOnDashboard.setter
    def vehicleDataOnDashboard(self, value):
        self.__chargerConfigModel.setAndSave('vehicle_data_on_dashboard', value)

    """
        returns the absolute path to the doc folder
    """
    @property
    def localDocDirectory(self) -> str:
        return os.path.join(self.oppleoRootDirectory, self.DOC_DIR_NAME)

oppleoConfig = OppleoConfig()