import logging
import socket
import re
import json
from enum import Enum
import threading
import time
from queue import Queue

from nl.oppleo.config.ChangeLog import changeLog
from nl.oppleo.models.Raspberry import Raspberry

from nl.oppleo.config.OppleoSystemConfig import OppleoSystemConfig
from nl.oppleo.config.OppleoConfig import OppleoConfig

from paho.mqtt import client as mqtt_client #, MQTTMessageInfo
from paho.mqtt.client import MQTTMessageInfo, MQTTv311, MQTTv5

from nl.oppleo.utils.OutboundEvent import OutboundEvent

from nl.oppleo.models.RfidModel import RfidModel
from nl.oppleo.models.ChargeSessionModel import ChargeSessionModel
from nl.oppleo.models.EnergyDeviceModel import EnergyDeviceModel
from nl.oppleo.models.EnergyDeviceMeasureModel import EnergyDeviceMeasureModel

from nl.oppleo.services.EvseState import EvseState, EvseStateName
from nl.oppleo.services.EvseOutput import EvseOutput


"""
    Start thread, connect upon enabled True in system-config
"""

oppleoSystemConfig = OppleoSystemConfig()
oppleoConfig = OppleoConfig()



class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class HomeAssistantMqttHandlerThread(object, metaclass=Singleton):
    __logger = logging.getLogger('nl.oppleo.services.HomeAssistantMqttHandlerThread')
    # functional syntax
    STATES = Enum('Status', ['CONNECTED', 'DISCONNECTED', 'CONNECT_FAILED', 'UNREACHABLE', 'NOT_AUTHORIZED', 'OTHER'])
    state = Enum('Status', ['OTHER']).OTHER
    mqttClient = None
    __client_id = None
    discovery_prefix = None
    object_id = None
    clean_session = True
    protocol = MQTTv311
    transport = "tcp"
    reconnect_on_failure = True
    isConnected = False
    keepalive = 60
    __most_recent_state = None
    __thread = None
    __threadLock = None
    __reconnectRequested = False
    __stateTopic = None
    # Create an emit queue, for other Threads to communicate to th ews emit background task
    __mqttMsgQueue = None
    __triggerAutoDiscover = False
    __haItems = []
    __selectedToken = None
    __MQTT_QOS_AT_MOST_ONCE = 0
    __MQTT_QOS_AT_LEAST_ONCE = 1
    __MQTT_QOS_EXACTLY_ONCE = 2
    # Home Assistance BLWT state
    __HA_STATES = Enum('State', ['UNKNOWN', 'ONLINE', 'OFFLINE'])
    ha_state = Enum('State', ['UNKNOWN']).UNKNOWN

    def __init__(self) -> None:
        super().__init__()

        self.__thread = None
        self.__threadLock = threading.Lock()
        self.__stop_event = threading.Event()

        self.__most_recent_state = dict()
        self.__mqttMsgQueue = Queue()
        self.state = self.STATES.OTHER



    def __defineHomeAssistanceItems__(self) -> list:

        rfidTokenList = list(map(lambda rfid: rfid.name if rfid.name != None and rfid.name != "" else rfid.rfid, RfidModel.get_all()))

        self.__haItems = [
            { "component": "sensor", "name": "ChargerID", "icon": "mdi:ev-station" },
            { "component": "sensor", "name": "EnergyDeviceID", "icon": "mdi:id-card" },
            { "component": "sensor", "name": "Timestamp", "icon": "mdi:calendar-month" },
            { "component": "sensor", "name": "A1", "icon": "mdi:sine-wave", "unit_of_measurement": "A" },
            { "component": "sensor", "name": "A2", "icon": "mdi:sine-wave", "unit_of_measurement": "A" },
            { "component": "sensor", "name": "A3", "icon": "mdi:sine-wave", "unit_of_measurement": "A" },
            { "component": "sensor", "name": "V1", "icon": "mdi:transmission-tower", "unit_of_measurement": "V" },
            { "component": "sensor", "name": "V2", "icon": "mdi:transmission-tower", "unit_of_measurement": "V" },
            { "component": "sensor", "name": "V3", "icon": "mdi:transmission-tower", "unit_of_measurement": "V" },
            { "component": "sensor", "name": "E1", "icon": "mdi:atom", "unit_of_measurement": "kWh" },
            { "component": "sensor", "name": "E2", "icon": "mdi:atom", "unit_of_measurement": "kWh" },
            { "component": "sensor", "name": "E3", "icon": "mdi:atom", "unit_of_measurement": "kWh" },
            { "component": "sensor", "name": "TotalEnergy", "icon": "mdi:atom", "unit_of_measurement": "kWh" },
            { "component": "sensor", "name": "P1", "icon": "mdi:rocket-launch-outline", "unit_of_measurement": "W" },
            { "component": "sensor", "name": "P2", "icon": "mdi:rocket-launch-outline", "unit_of_measurement": "W" },
            { "component": "sensor", "name": "P3", "icon": "mdi:rocket-launch-outline", "unit_of_measurement": "W" },
            { "component": "sensor", "name": "Frequency", "icon": "mdi:sine-wave", "unit_of_measurement": "Hz" },
            { "component": "sensor", "name": "ChargeSpeed", "icon": "mdi:car-speed-limiter", "unit_of_measurement": "km" },
            { "component": "sensor", "name": "Status", "icon": "mdi:clipboard-edit-outline" },
            { "component": "sensor", "name": "Energy", "icon": "mdi:atom", "unit_of_measurement": "kWh" },
            { "component": "sensor", "name": "Cost", "icon": "mdi:currency-eur", "unit_of_measurement": "€" },
            { "component": "sensor", "name": "Token", "icon": "mdi:credit-card-scan" },
            { "component": "sensor", "name": "EVSE", "icon": "mdi:home-battery-outline" },
            { "component": "sensor", "name": "OffPeak", "icon": "mdi:clock-check-outline" },
            { "component": "sensor", "name": "Charging", "icon": "mdi:clipboard-pulse-outline" },
            { "component": "sensor", "name": "StartValue", "icon": "mdi:gauge-empty", "unit_of_measurement": "kWh"  },
            { "component": "sensor", "name": "EndValue", "icon": "mdi:gauge-full", "unit_of_measurement": "kWh"  },
            { "component": "sensor", "name": "Trigger", "icon": "mdi:ray-start-arrow" },
            { "component": "sensor", "name": "Tariff", "icon": "mdi:currency-eur", "unit_of_measurement": "€" },
            { "component": "select", "name": "Token", "icon": "mdi:credit-card-scan", "options": rfidTokenList }
        ]


    def start(self):
        self.__stop_event.clear()
        self.__logger.debug('Launching HomeAssistant Mqtt Thread...')

        self.__thread = threading.Thread(target=self.__loop__, name='HomeAssistantMqttThread')
        self.__thread.start()


    def is_alive(self):
        return False if self.__thread == None else self.__thread.is_alive()


    def __loop__(self):
        global oppleoSystemConfig

        self.__triggerAutoDiscover = True
        self.__triggerMostRecent = True

        while not self.__stop_event.is_set():

            if oppleoSystemConfig.homeAssistantMqttEnabled:

                if self.__reconnectRequested:
                    HomeAssistantMqttHandlerThread.__logger.debug("Requesting reconnect from HomeAssistant MQTT Broker...")
                    with self.__threadLock:
                        self.disconnect()
                        self.__reconnectRequested = False
                    time.sleep(0.5)

                if not self.isConnected:
                    # Retry in 5, 4, 3, 2, ...
                    self.connect()
                    time.sleep(0.75)

                if self.isConnected:
                    # Need to send Auto Discover messages?
                    if self.__triggerAutoDiscover:
                        with self.__threadLock:
                            self.__triggerAutoDiscover = False
                        self.__sendAutoDiscover()

                    if self.__triggerMostRecent:
                        with self.__threadLock:
                            self.__triggerMostRecent = False
                        self.__sync_open_session()
                        # json.dumps(s, default=str) -- overcomes "TypeError: Object of type 'datetime' is not JSON serializable"
                        self.__publish__(topic=self.__stateTopic, message=json.dumps(self.__most_recent_state, default=str), notify=False)
                        # TODO
                        # Re-trigger last Modbus Read
                        energyDeviceMeasureModel = EnergyDeviceMeasureModel()
                        energy_device_data = EnergyDeviceModel.get()
                        if energy_device_data is not None:
                            last_save_measurement = energyDeviceMeasureModel.get_last_saved(energy_device_data.energy_device_id)
                            self.energyUpdate(device_measurement=last_save_measurement)
                        # Trigger last known EVSE status
                        evseOutput = EvseOutput()
                        if oppleoConfig.chThread is not None and oppleoConfig.chThread.is_status_charging:
                            self.sessionUpdate(evse_state=EvseState.EVSE_STATE_CHARGING)
                        elif evseOutput.is_enabled():
                            self.sessionUpdate(evse_state=EvseState.EVSE_STATE_CONNECTED)
                        else:
                            self.sessionUpdate(evse_state=EvseState.EVSE_STATE_INACTIVE)

                    if not self.__mqttMsgQueue.empty():
                        # Blocking call, make sure there is a message to obtain
                        msg = self.__mqttMsgQueue.get()
                        # json.dumps(s, default=str) -- overcomes "TypeError: Object of type 'datetime' is not JSON serializable"
                        self.__publish__(topic=self.__stateTopic, message=json.dumps(msg, default=str), notify=False)

            else:
                HomeAssistantMqttHandlerThread.__logger.debug("HomeAssistant MQTT Broker connection not enabled.")
                if self.state not in [self.STATES.DISCONNECTED, self.STATES.NOT_AUTHORIZED]:

                    if self.state == self.STATES.CONNECTED:
                        HomeAssistantMqttHandlerThread.__logger.debug("HomeAssistant MQTT Broker connected, disconnecting...")
                        self.disconnect()
                    else:
                        self.state = self.STATES.DISCONNECTED
                        OutboundEvent.triggerEvent(
                            event='ha_mqtt_status_update', 
                            id=oppleoConfig.chargerID,
                            data={ "state": self.state.name },
                            namespace='/settings',
                            public=True
                        )


            # TODO
            # - read MQTT, check for WILL messages







            # Sleep to allow other threads
            time.sleep(0.75)
        HomeAssistantMqttHandlerThread.__logger.warning("HomeAssistant MQTT Broker connect Thread stopping...")


    def stop(self, block=False):
        self.__logger.debug('.stop() - Requested to stop')
        #if self.__thread is not None:
        #    self.__thread.stop()
        self.__stop_event.set()

    # Call reconnect if configuration is changed
    def reconnect(self):
        with self.__threadLock:
            self.__reconnectRequested = True


    # https://stackoverflow.com/questions/36093078/mqtt-is-there-a-way-to-check-if-the-client-is-still-connected
    def connect(self) -> None:
        global oppleoSystemConfig, oppleoConfig

        self.__logger.debug("Connecting to HomeAssistant MQTT Broker...")

        def __on_connect__(client, userdata, flags, rc):
            # This function does not have access to the self object
            homeAssistantMqttHandlerThread = HomeAssistantMqttHandlerThread()
            if rc == 0:
                homeAssistantMqttHandlerThread.isConnected = True
                homeAssistantMqttHandlerThread.__logger.info("Connected to HomeAssistant MQTT Broker.")
                homeAssistantMqttHandlerThread.state = self.STATES.CONNECTED

                """
                BIRTH AND LAST WILL MESSAGES
                Home Assistant’s supports Birth and Last Will and Testament (LWT) messages to send a message after the service has started, and to notify other clients about a disconnected client. 
                The LWT message will be sent on clean (shut-down), on unclean (crashing or losing connection) disconnect.
                By default, Home Assistant sends online and offline to homeassistant/status.
                """
                client.subscribe((oppleoSystemConfig.homeAssistantMqttBirthAndLastWillAndTestament, homeAssistantMqttHandlerThread.__MQTT_QOS_EXACTLY_ONCE))

                """
                COMMAND TOPICS
                Subscribe to all command topics.
                """
                homeAssistantMqttHandlerThread.__defineHomeAssistanceItems__()
                for item in homeAssistantMqttHandlerThread.__haItems:
                    if item['component'] in ["select"]:
                        uniqueId = self.object_id + "_" + item["name"]
                        command_topic = self.discovery_prefix + '/' + item['component'] + '/' + uniqueId + '/select'
                        client.subscribe((command_topic, homeAssistantMqttHandlerThread.__MQTT_QOS_EXACTLY_ONCE))

                OutboundEvent.triggerEvent(
                    event='ha_mqtt_status_update', 
                    id=oppleoConfig.chargerID,
                    data={ "state": homeAssistantMqttHandlerThread.state.name },
                    namespace='/settings',
                    public=True
                )

            elif rc == 5:
                if homeAssistantMqttHandlerThread.isConnected or \
                   homeAssistantMqttHandlerThread.state != homeAssistantMqttHandlerThread.STATES.NOT_AUTHORIZED:
                    homeAssistantMqttHandlerThread.isConnected = False
                    homeAssistantMqttHandlerThread.__logger.warn("Connecting to HomeAssistant MQTT Broker failed (NOT AUTHORIZED) [1 rc={rc}].".format(rc=rc))
                    homeAssistantMqttHandlerThread.state = homeAssistantMqttHandlerThread.STATES.NOT_AUTHORIZED
                    oppleoSystemConfig.homeAssistantMqttEnabled = False
                    OutboundEvent.triggerEvent(
                        event='ha_mqtt_status_update', 
                        id=oppleoConfig.chargerID,
                        data={ "state": homeAssistantMqttHandlerThread.state.name },
                        namespace='/settings',
                        public=True
                    )
            else:
                if homeAssistantMqttHandlerThread.isConnected or homeAssistantMqttHandlerThread.state != homeAssistantMqttHandlerThread.STATES.CONNECT_FAILED:
                    homeAssistantMqttHandlerThread.isConnected = False
                    homeAssistantMqttHandlerThread.__logger.warn("Connecting to HomeAssistant MQTT Broker failed [1 rc={rc}].".format(rc=rc))
                    homeAssistantMqttHandlerThread.state = homeAssistantMqttHandlerThread.STATES.CONNECT_FAILED
                    OutboundEvent.triggerEvent(
                            event='ha_mqtt_status_update', 
                            id=oppleoConfig.chargerID,
                            data={ "state": homeAssistantMqttHandlerThread.state.name },
                            namespace='/settings',
                            public=True
                        )
        
        def __on_disconnect__(client, userdata, rc):
            homeAssistantMqttHandlerThread = HomeAssistantMqttHandlerThread()
            if homeAssistantMqttHandlerThread.isConnected or \
                homeAssistantMqttHandlerThread.state not in [homeAssistantMqttHandlerThread.STATES.DISCONNECTED, 
                                                            homeAssistantMqttHandlerThread.STATES.NOT_AUTHORIZED]:
                homeAssistantMqttHandlerThread.__logger.warn("Disconnected from HomeAssistant MQTT Broker [rc={rc}].".format(rc=rc))
                homeAssistantMqttHandlerThread.isConnected = False
                homeAssistantMqttHandlerThread.state = homeAssistantMqttHandlerThread.STATES.DISCONNECTED
                OutboundEvent.triggerEvent(
                        event='ha_mqtt_status_update', 
                        id=oppleoConfig.chargerID,
                        data={ "state": homeAssistantMqttHandlerThread.state.name },
                        namespace='/settings',
                        public=True
                    )


        def __on_connect_fail__(client, userdata, rc):
            homeAssistantMqttHandlerThread = HomeAssistantMqttHandlerThread()
            if homeAssistantMqttHandlerThread.isConnected or homeAssistantMqttHandlerThread.state != homeAssistantMqttHandlerThread.STATES.CONNECT_FAILED:
                homeAssistantMqttHandlerThread.__logger.warn("Connecting to HomeAssistant MQTT Broker failed [2 rc={rc}].".format(rc=rc))
                homeAssistantMqttHandlerThread.isConnected = False
                homeAssistantMqttHandlerThread.state = homeAssistantMqttHandlerThread.STATES.CONNECT_FAILED
                OutboundEvent.triggerEvent(
                        event='ha_mqtt_status_update', 
                        id=oppleoConfig.chargerID,
                        data={ "state": homeAssistantMqttHandlerThread.state.name },
                        namespace='/settings',
                        public=True
                    )

        def __on_subscribe__(client, userdata, mid, granted_qos):
            homeAssistantMqttHandlerThread = HomeAssistantMqttHandlerThread()
            homeAssistantMqttHandlerThread.__logger.warn("HomeAssistant MQTT Broker - subscribed [client={client}, userdata={userdata}, mid={mid}, granted_qos={granted_qos}].".format(client=client, userdata=userdata, mid=mid, granted_qos=granted_qos))
            pass
        def __on_unsubscribe__(client, userdata, mid):
            homeAssistantMqttHandlerThread = HomeAssistantMqttHandlerThread()
            homeAssistantMqttHandlerThread.__logger.warn("HomeAssistant MQTT Broker - unsubscribed [client={client}, userdata={userdata}, mid={mid}].".format(client=client, userdata=userdata, mid=mid))
            pass

        def __on_message__(client, userdata, message):
            homeAssistantMqttHandlerThread = HomeAssistantMqttHandlerThread()
            homeAssistantMqttHandlerThread.__logger.warn("HomeAssistant MQTT Broker - message [client={client}, userdata={userdata}, message={message}].".format(client=client, userdata=userdata, message=message))

            # BLWT
            if message.topic == oppleoSystemConfig.homeAssistantMqttBirthAndLastWillAndTestament:
                # Birt or Last Will and Testament message
                homeAssistantMqttHandlerThread.__logger.debug("HomeAssistant MQTT Broker - BLWT message {msg}".format(msg=message.payload.decode("utf-8")))
                if message.payload.decode("utf-8").upper() == "ONLINE":
                    # HA has come online
                    homeAssistantMqttHandlerThread.ha_state = homeAssistantMqttHandlerThread.__HA_STATES.ONLINE
                    OutboundEvent.triggerEvent(
                        event='ha_mqtt_ha_status', 
                        id=oppleoConfig.chargerID,
                        namespace='/settings',
                        data={ "state": homeAssistantMqttHandlerThread.ha_state.name },
                        public=False
                    )
                    # Send auto discover messages
                    homeAssistantMqttHandlerThread.triggerAutoDiscover()
                    # (re-)Send latest values
                    homeAssistantMqttHandlerThread.triggerMostRecent()
                elif message.payload.decode("utf-8").upper() == "OFFLINE":
                    homeAssistantMqttHandlerThread.ha_state = homeAssistantMqttHandlerThread.__HA_STATES.OFFLINE
                    OutboundEvent.triggerEvent(
                        event='ha_mqtt_ha_status', 
                        id=oppleoConfig.chargerID,
                        namespace='/settings',
                        data={ "state": homeAssistantMqttHandlerThread.ha_state.name },
                        public=False
                    )
                else:
                    homeAssistantMqttHandlerThread.__logger.warn("HomeAssistant MQTT Broker - BLWT message {msg} not understood (expecting online or offline)".format(msg=message.payload.decode("utf-8")))
                    homeAssistantMqttHandlerThread.ha_state = homeAssistantMqttHandlerThread.__HA_STATES.UNKNOWN
                    OutboundEvent.triggerEvent(
                        event='ha_mqtt_ha_status', 
                        id=oppleoConfig.chargerID,
                        namespace='/settings',
                        data={ "state": homeAssistantMqttHandlerThread.ha_state.name },
                        public=False
                    )

                # Done
                return

            key = message.topic.split('/')[2].split('_')[1] 
            homeAssistantMqttHandlerThread.__logger.warn("HomeAssistant MQTT Broker - message [key={key}].".format(key=key))

            # homeassistant/select/OPPLEOA001N01_Token/select
            key = message.topic.split('/')[2].split('_')[1] 
            homeAssistantMqttHandlerThread.__logger.warn("HomeAssistant MQTT Broker - message [key={key}].".format(key=key))
            if key == "Token":
                homeAssistantMqttHandlerThread.__logger.debug("HomeAssistant MQTT Broker - Request to switch token to {rToken}...".format(rToken=message.payload.decode("utf-8")))

                # Check if there was a charge session active when Oppleo was stopped.
                openChargeSession = ChargeSessionModel.getOpenChargeSession(device=oppleoConfig.chargerID)
                if openChargeSession is not None:
                    # A session is active, the token cannot be switched - switch back
                    homeAssistantMqttHandlerThread.__logger.warn("HomeAssistant MQTT Broker - cannot switch to token {rToken} during active charge session.".format(rToken=message.payload.decode("utf-8")))
                    homeAssistantMqttHandlerThread.publish({'Token': (openChargeSession.rfid.name if openChargeSession.rfid.name != None and openChargeSession.rfid.name != "" else openChargeSession.rfid.rfid)})
                    return
                
                # No active charge session - Find the selected Token
                rfidCards = RfidModel.get_all()
                selectedRfid = None
                # Find by name
                selectedRfid = next((rfid for rfid in list(filter(lambda rfid: rfid.name == message.payload.decode("utf-8"), rfidCards)) if rfid), None)
                if selectedRfid is None:
                    # Find by ID
                    selectedRfid = next((rfid for rfid in list(filter(lambda rfid: rfid.rfid == message.payload.decode("utf-8"), rfidCards)) if rfid), None)

                # If not found there is a consistency issue, revert
                if selectedRfid is None:
                    HomeAssistantMqttHandlerThread.__logger.warn("HomeAssistant MQTT Broker - cannot switch to non exixstend token {rToken}.".format(rToken=message.payload.decode("utf-8")))
                    self.__selectedToken = None
                    return

                # This token is the new selected token, announce
                self.__selectedToken = selectedRfid
                homeAssistantMqttHandlerThread.publish({'Token': (selectedRfid.name if selectedRfid.name != None and selectedRfid.name != "" else selectedRfid.rfid)})



            print("received message =",str(message.payload.decode("utf-8")))
            data = "{'" + str(message.payload) + "', " + str(message.topic) + "}"
            print("received message = {}".format(data) )
            # Is this a Birth message from Home Assistant?
            # - if so send a Discovery and send Last Status

            # Is this a Last Will and testament message from Home Assistant?
            # - notify connection lost due to Last Will and Testament

            pass

        if oppleoSystemConfig.homeAssistantMqttClientId != None and oppleoSystemConfig.homeAssistantMqttClientId != '':
            self.__client_id = oppleoSystemConfig.homeAssistantMqttClientId
        else:
            self.__client_id = 'Oppleo_' + oppleoSystemConfig.chargerID
        self.discovery_prefix = oppleoSystemConfig.homeAssistantMqttDiscoveryPrefix

        # Only alphanumerics, underscore and hyphen allowed in object ID
        self.object_id = re.sub(r'[^A-Za-z0-9_-]', '', oppleoSystemConfig.chargerID)

        # Set Connecting Client ID
        self.mqttClient = mqtt_client.Client(client_id = self.__client_id, 
                                             clean_session= self.clean_session,
                                             protocol = self.protocol,
                                             transport = self.transport,
                                             reconnect_on_failure = self.reconnect_on_failure
                                            )
        self.mqttClient.on_connect = __on_connect__
        self.mqttClient.on_disconnect = __on_disconnect__
        self.mqttClient.on_connect_fail = __on_connect_fail__
        self.mqttClient.on_subscribe = __on_subscribe__
        self.mqttClient.on_unsubscribe = __on_unsubscribe__
        self.mqttClient.on_message = __on_message__

        self.__set_user__()

        try:
            self.mqttClient.connect(host = oppleoSystemConfig.homeAssistantMqttHost, 
                                    port = oppleoSystemConfig.homeAssistantMqttPort,
                                    keepalive = self.keepalive)
        except socket.timeout:
            self.__logger.warn("Socket timeout connecting to HomeAssistant MQTT Broker...")
            if self.state != self.STATES.UNREACHABLE:
                self.state = self.STATES.UNREACHABLE
                OutboundEvent.triggerEvent(
                        event='ha_mqtt_status_update', 
                        id=oppleoConfig.chargerID,
                        data={ "state": self.state.name },
                        namespace='/settings',
                        public=True
                    )


        self.mqttClient.loop_start()

        # State announcement always as sensor
        self.__stateTopic = ''+self.discovery_prefix+'/sensor/'+self.object_id+'/state'
        

    def triggerAutoDiscover(self) -> None:
        with self.__threadLock:
            self.__triggerAutoDiscover = True


    def triggerMostRecent(self) -> None:
        with self.__threadLock:
            self.__triggerMostRecent = True


    def __sendAutoDiscover(self) -> bool:
        global oppleoConfig

        HomeAssistantMqttHandlerThread.__logger.debug("Sending Auto-Discover config messages to HomeAssistant MQTT Broker...")

        if not self.isConnected:
            HomeAssistantMqttHandlerThread.__logger.warn("Cannot send Auto-Discover config messages to HomeAssistant MQTT Broker, not connected.")
            return False

        r = Raspberry()

        # (Re)define the items for AutoDiscovery
        self.__defineHomeAssistanceItems__()

        for item in self.__haItems:
            uniqueId = self.object_id + "_" + item["name"]
            configTopic = self.discovery_prefix + '/' + item['component'] + '/' + uniqueId + '/config'

            msg = {}
            # Sensor
            msg['name'] = item["name"]
            # States
            if item['component'] in ["sensor"]:
                msg['state_topic'] = self.discovery_prefix + '/' + item['component'] + '/' + self.object_id + '/state'
            # Commands
            if item['component'] in ["select"]:
                msg['command_topic'] = self.discovery_prefix + '/' + item['component'] + '/' + uniqueId + '/select'
                msg['state_topic'] = self.discovery_prefix + '/' + 'sensor' + '/' + self.object_id + '/state'
            
            msg['unique_id'] = uniqueId
            if "icon" in item:
                msg['icon'] = item["icon"]
            if "unit_of_measurement" in item:
                msg['unit_of_measurement'] = item["unit_of_measurement"]
            msg['value_template'] = "{{ value_json."+item["name"]+" }}"
            if "options" in item:
                msg['options'] = item["options"]

            # Part of the device
            msg['device'] = {}
            msg['device']['identifiers'] = []
            msg['device']['identifiers'].append(self.object_id)
            msg['device']['name'] = oppleoConfig.chargerNameText
            msg['device']['manufacturer'] = "Oppleo"
            msg['device']['model'] = r.get_model()
            #msg['device']['configuration_url'] = "http://192.168.2.160"
            msg['device']['sw_version'] = changeLog.currentVersionStr

            # json.dumps(s, default=str) -- overcomes "TypeError: Object of type 'datetime' is not JSON serializable"
            HomeAssistantMqttHandlerThread.__logger.debug("HA MQTT sending {} to {}.".format(json.dumps(msg, default=str), configTopic))
            self.__publish__(topic=configTopic, message=json.dumps(msg), notify=False)


        OutboundEvent.triggerEvent(
            event='ha_mqtt_autodiscover', 
            id=oppleoConfig.chargerID,
            data={},
            namespace='/settings',
            public=True
        )


    def disconnect(self) -> None:
        HomeAssistantMqttHandlerThread.__logger.debug("Requesting disconnect from HomeAssistant MQTT Broker...")
        if self.isConnected:
            HomeAssistantMqttHandlerThread.__logger.debug("Disconnecting from HomeAssistant MQTT Broker...")
            self.mqttClient.disconnect()

    def __set_user__(self) -> None:
        global oppleoSystemConfig

        if oppleoSystemConfig.homeAssistantMqttUsername is not None and oppleoSystemConfig.homeAssistantMqttUsername != "": 
            HomeAssistantMqttHandlerThread.__logger.debug("Setting user for HomeAssistant MQTT Broker to {}...".format(oppleoSystemConfig.homeAssistantMqttUsername))
            self.mqttClient.username_pw_set( oppleoSystemConfig.homeAssistantMqttUsername, 
                                             oppleoSystemConfig.homeAssistantMqttPassword if oppleoSystemConfig.homeAssistantMqttPassword is not None and oppleoSystemConfig.homeAssistantMqttPassword != "" else None
                                            )
    

  
    def publish(self, values:dict=None) -> None:
        HomeAssistantMqttHandlerThread.__logger.debug("Sending status update messages to HomeAssistant MQTT Broker...")

        # Maintain the most recent values
        # Python 3.10
        # self.__most_recent_state = self.__most_recent_state | values
        # Python < 3.10
        self.__most_recent_state = {k: v for d in [self.__most_recent_state, values] for k, v in d.items()}

        if self.__mqttMsgQueue is not None:
            self.__mqttMsgQueue.put( self.__most_recent_state )



    """
        timeout in ms
    """
    def __publish__(self, topic:str='homeassistant', message:str=None, waitForPublish:bool=False, timeout:int=1000, notify:bool=True) -> bool:
        global oppleoConfig

        HomeAssistantMqttHandlerThread.__logger.debug(f'Publish msg {message} to HomeAssistant topic {topic} ... ')

        if not self.isConnected:
            HomeAssistantMqttHandlerThread.__logger.warn("Cannot publish status message to HomeAssistant MQTT Broker, not connected.")
            return False

        # Can be async connected, with self.mqttClient.is_connected() returning false...

        #        if not self.mqttClient.is_connected():
        #            OppleoMqttClient.__logger.warn(f'Failed to publish msg {message} to topic {topic}, not connected')
        #            return False
            
        HomeAssistantMqttHandlerThread.__logger.debug(f'Publishing HomeAssistant MQTT msg {message} to topic {topic}')
        
        data = {}
        data['topic'] = topic
        data['message'] = message

        try:
            homeAssistantMqttMessageInfo = self.mqttClient.publish(topic=topic, payload=message)
            if notify:
                OutboundEvent.triggerEvent(
                    event='ha_mqtt_message_send', 
                    id=oppleoConfig.chargerID,
                    data=json.dumps(data, default=str),
                    namespace='/settings',
                    public=False
                )            
            if waitForPublish:
                homeAssistantMqttMessageInfo.wait_for_publish(timeout=(timeout/1000))
        except (ValueError, TypeError, RuntimeError) as e:
            return False
        return homeAssistantMqttMessageInfo.is_published()


    # Callback from MeasureElectricityUsageThread with updated EnergyDeviceMeasureModel
    def energyUpdate(self, device_measurement:EnergyDeviceMeasureModel=None):
        self.__logger.debug('.energyUpdate() callback...')

        # convert into JSON:
        measurement = device_measurement.to_dict()
        translation = { "energy_device_id": "EnergyDeviceID",
                        "created_at": "Timestamp",
                        "kwh_l1": "E1",
                        "kwh_l2": "E2",
                        "kwh_l3": "E3",
                        "a_l1": "A1",
                        "a_l2": "A2",
                        "a_l3": "A3",
                        "p_l1": "P1",
                        "p_l2": "P2",
                        "p_l3": "P3",
                        "v_l1": "V1",
                        "v_l2": "V2",
                        "v_l3": "V3",
                        "kw_total": "TotalEnergy",
                        "hz": "Frequency"
                }
        translated_measurement = {}
        for item, value in translation.items():
            translated_measurement[value] = measurement[item]

        translated_measurement['ChargeSpeed'] = str(round( 
                    (
                        (
                            (float(measurement['p_l1']) if 'p_l1' in measurement else 0.0) +
                            (float(measurement['p_l2']) if 'p_l2' in measurement else 0.0) +
                            (float(measurement['p_l3']) if 'p_l3' in measurement else 0.0)
                        )
                        / oppleoConfig.factorWhkm
                    ),
                    1   # 1 decimal
                ))

        self.publish( values=translated_measurement )

    # TODO: Standardize the session status
    def sessionUpdate(self, status:str=None, energy:float=None, cost:float=None, token:str=None, offpeak:bool=None, charging:bool=None, 
                      vehicle:str=None, start_value:float=None, end_value:float=None, trigger:str=None, tariff:float=None, evse_state:EvseState=None):
        self.__logger.debug('.sessionUpdate()...')

        sessionInfo = {}

        sessionInfo['ChargerID'] = oppleoConfig.chargerID

        if status is not None:
            sessionInfo['Status'] = status
        if energy is not None:
            sessionInfo['Energy'] = round( energy, 1 )
        if start_value is not None:
            sessionInfo['StartValue'] = round( start_value, 1 )
        if end_value is not None:
            sessionInfo['EndValue'] = round( end_value, 1 )
        if trigger is not None:
            sessionInfo['Trigger'] = trigger
        if tariff is not None:
            sessionInfo['Tariff'] = round( tariff, 2 ) 
        if cost is not None:
            sessionInfo['Cost'] = round( cost, 2 )
        if token is not None:
            sessionInfo['Token'] = token
        if evse_state is not None:
            sessionInfo['EVSE'] = EvseStateName(evse_state)
        if offpeak is not None:
            sessionInfo['OffPeak'] = offpeak
        if charging is not None:
            sessionInfo['Charging'] = charging
        if vehicle is not None:
            sessionInfo['Vehicle'] = vehicle

        self.publish( values=sessionInfo )



    def __sync_open_session(self):
        self.__logger.debug('.__sync_open_session()')

        # Get session info or reset
        openSession = ChargeSessionModel.getOpenChargeSession(oppleoConfig.chargerID)
        if openSession is not None:
            self.__logger.debug('Open session: {}'.format(openSession.to_str()))
            rfid = RfidModel.get_one(rfid=openSession.rfid)
            # Open session
            self.__most_recent_state['Status'] = 'Waiting'
            self.__most_recent_state['StartTime'] = openSession.start_time
            self.__most_recent_state['StartValue'] = openSession.start_value
            self.__most_recent_state['EndValue'] = openSession.end_value
            self.__most_recent_state['EnergyDeviceID'] = openSession.energy_device_id
            self.__most_recent_state['km'] = openSession.km
            self.__most_recent_state['Energy'] = openSession.total_energy
            self.__most_recent_state['Cost'] = openSession.total_price
            self.__most_recent_state['Trigger'] = openSession.trigger
            self.__most_recent_state['Tariff'] = openSession.tariff
            self.__most_recent_state['Token'] = rfid.name if rfid.name != None and rfid.name != "" else rfid.rfid
            self.__most_recent_state['Charging'] = False
            self.__most_recent_state['EVSE'] = "TBD"
        else:
            self.__logger.debug('No open session')
            # No charge session
            self.__most_recent_state['Status'] = 'No active session'
            self.__most_recent_state['StartTime'] = ''
            self.__most_recent_state['StartValue'] = 0
            self.__most_recent_state['EndValue'] = 0
            self.__most_recent_state['EnergyDeviceID'] = oppleoConfig.chargerID
            self.__most_recent_state['km'] = 0
            self.__most_recent_state['Energy'] = 0
            self.__most_recent_state['Cost'] = 0
            self.__most_recent_state['Trigger'] = '-'
            self.__most_recent_state['Tariff'] = 0
            self.__most_recent_state['Token'] = ''
            self.__most_recent_state['Charging'] = False
            self.__most_recent_state['EVSE'] = ''

        self.__most_recent_state['OffPeak'] = oppleoConfig.offpeakEnabled



    def diag(self):
        return json.dumps({
            "state": "-" if self.state is None else self.state.name,
            "discovery_prefix": "-" if self.discovery_prefix is None else self.discovery_prefix,
            "object_id": "-" if self.object_id is None else self.object_id,
            "clean_session": self.clean_session,
            "protocol": self.protocol,
            "transport": self.transport,
            "reconnect_on_failure": self.reconnect_on_failure,
            "isConnected": self.isConnected,
            "keepalive": self.keepalive,
            "__selectedToken": "-" if self.__selectedToken is None else self.__selectedToken,
            "ha_state": "-" if self.ha_state is None else self.ha_state.name,
            "__haItems": self.__haItems,
            "__triggerAutoDiscover": self.__triggerAutoDiscover,
            "__stateTopic": "-" if self.__stateTopic is None else self.__stateTopic,
            "__reconnectRequested": self.__reconnectRequested,
            "__most_recent_state": self.__most_recent_state
            }, 
            default=str     # Overcome "TypeError: Object of type datetime is not JSON serializable"
        )
