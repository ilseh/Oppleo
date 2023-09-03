import logging
from nl.oppleo.config.OppleoSystemConfig import OppleoSystemConfig

from paho.mqtt import client as mqtt_client #, MQTTMessageInfo
from paho.mqtt.client import MQTTMessageInfo, MQTTv311, MQTTv5

oppleoSystemConfig = OppleoSystemConfig()


class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class HomeAssistantMqttClient(object, metaclass=Singleton):
    logger = logging.getLogger('nl.oppleo.services.HomeAssistantMqttClient')
    homeAssistantMqttClient = None

    def __init__(self) -> None:
        super().__init__()
        # Set Connecting Client ID
        self.homeAssistantMqttClient = mqtt_client.Client(client_id='Oppleo_'+oppleoSystemConfig.chargerID, 
                                                          clean_session=True,
                                                          protocol=MQTTv311,
                                                          transport="tcp",
                                                          reconnect_on_failure=True
                                                        )
        self.setUser()


    def connect(self) -> None:
        HomeAssistantMqttClient.logger.debug("Connecting to HomeAssistant MQTT Broker...")
        self.homeAssistantMqttClient.connect(host=oppleoSystemConfig.homeAssistantMqttHost, port=oppleoSystemConfig.homeAssistantMqttPort)
        self.homeAssistantMqttClient.loop_start()
        if self.is_connected:
            self.sendAutoDiscover()

    def sendAutoDiscover(self) -> None:
        global oppleoSystemConfig

        HomeAssistantMqttClient.logger.debug("Sending Auto-Discover config messages to HomeAssistant MQTT Broker...")

        """
            TODO
            - send auto discover
            - trigger from enable on settings page
        """
        configTopic = 'homeassistant/sensor/'+oppleoSystemConfig.chargerID+'/config'

        # The energy device
        A1 = '{"device_class": "sensor”, "state_topic": "homeassistant/sensor/'+oppleoSystemConfig.chargerID+'/state", "unit_of_measurement": “A", "value_template": "{{ value_json.A1}}","unique_id": “A1", "device": {"identifiers": [“'+oppleoSystemConfig.chargerID+'_A1"], "name": “A1” }}'
        self.publish(topic=configTopic, message=A1)
        A2 = '{"device_class": "sensor”, "state_topic": "homeassistant/sensor/'+oppleoSystemConfig.chargerID+'/state", "unit_of_measurement": “A", "value_template": "{{ value_json.A2}}”,”unique_id": “A2”, "device": {"identifiers": [“'+oppleoSystemConfig.chargerID+'_A2”], "name": “A2” }}'
        self.publish(topic=configTopic, message=A2)
        A3 = '{"device_class": "sensor”, "state_topic": "homeassistant/sensor/'+oppleoSystemConfig.chargerID+'/state", "unit_of_measurement": “A", "value_template": "{{ value_json.A3}}”,”unique_id": “A3”, "device": {"identifiers": [“'+oppleoSystemConfig.chargerID+'_A3”], "name": “A3” }}'
        self.publish(topic=configTopic, message=A3)

        V1 = '{"device_class": "sensor”, "state_topic": "homeassistant/sensor/'+oppleoSystemConfig.chargerID+'/state", "unit_of_measurement": “V”, "value_template": "{{ value_json.V1}}”,”unique_id": “V1”, "device": {"identifiers": [“'+oppleoSystemConfig.chargerID+'_V1”], "name": “V1” }}'
        self.publish(topic=configTopic, message=V1)
        V2 = '{"device_class": "sensor”, "state_topic": "homeassistant/sensor/'+oppleoSystemConfig.chargerID+'/state", "unit_of_measurement": “V”, "value_template": "{{ value_json.V2}}”,”unique_id": “V2”, "device": {"identifiers": [“'+oppleoSystemConfig.chargerID+'_V2”], "name": “V2” }}'
        self.publish(topic=configTopic, message=V2)
        V3 = '{"device_class": "sensor”, "state_topic": "homeassistant/sensor/'+oppleoSystemConfig.chargerID+'/state", "unit_of_measurement": “V”, "value_template": "{{ value_json.V3}}”,”unique_id": “V3”, "device": {"identifiers": [“'+oppleoSystemConfig.chargerID+'_V3”], "name": “V3” }}'
        self.publish(topic=configTopic, message=V3)

        E1 = '{"device_class": "sensor”, "state_topic": "homeassistant/sensor/'+oppleoSystemConfig.chargerID+'/state", "unit_of_measurement": “kWh”, "value_template": "{{ value_json.E1}}”,”unique_id": “E1”, "device": {"identifiers": [“'+oppleoSystemConfig.chargerID+'_E1”], "name": “E1” }}'
        self.publish(topic=configTopic, message=E1)
        E2 = '{"device_class": "sensor”, "state_topic": "homeassistant/sensor/'+oppleoSystemConfig.chargerID+'/state", "unit_of_measurement": “kWh”, "value_template": "{{ value_json.E2}}”,”unique_id": “E2”, "device": {"identifiers": [“'+oppleoSystemConfig.chargerID+'_E2”], "name": “E2” }}'
        self.publish(topic=configTopic, message=E2)
        E3 = '{"device_class": "sensor”, "state_topic": "homeassistant/sensor/'+oppleoSystemConfig.chargerID+'/state", "unit_of_measurement": “kWh”, "value_template": "{{ value_json.E3}}”,”unique_id": “E3”, "device": {"identifiers": [“'+oppleoSystemConfig.chargerID+'_E3”], "name": “E3” }}'
        self.publish(topic=configTopic, message=E3)

        ET = '{"device_class": "sensor”, "state_topic": "homeassistant/sensor/'+oppleoSystemConfig.chargerID+'/state", "unit_of_measurement": “kWh”, "value_template": "{{ value_json.ET}}”,”unique_id": “Energy”, "device": {"identifiers": [“'+oppleoSystemConfig.chargerID+'_ET”], "name": “Total Energy” }}'
        self.publish(topic=configTopic, message=ET)

        P1 = '{"device_class": "sensor”, "state_topic": "homeassistant/sensor/'+oppleoSystemConfig.chargerID+'/state", "unit_of_measurement": “W”, "value_template": "{{ value_json.P1}}”,”unique_id": “P1”, "device": {"identifiers": [“'+oppleoSystemConfig.chargerID+'_P1”], "name": “P1” }}'
        self.publish(topic=configTopic, message=P1)
        P2 = '{"device_class": "sensor”, "state_topic": "homeassistant/sensor/'+oppleoSystemConfig.chargerID+'/state", "unit_of_measurement": “W”, "value_template": "{{ value_json.P2}}”,”unique_id": “P2”, "device": {"identifiers": [“'+oppleoSystemConfig.chargerID+'_P2”], "name": “P2” }}'
        self.publish(topic=configTopic, message=P2)
        P3 = '{"device_class": "sensor”, "state_topic": "homeassistant/sensor/'+oppleoSystemConfig.chargerID+'/state", "unit_of_measurement": “W”, "value_template": "{{ value_json.P3}}”,”unique_id": “P3”, "device": {"identifiers": [“'+oppleoSystemConfig.chargerID+'_P3”], "name": “P3” }}'
        self.publish(topic=configTopic, message=P3)

        FREQ = '{"device_class": "sensor”, "state_topic": "homeassistant/sensor/'+oppleoSystemConfig.chargerID+'/state", "unit_of_measurement": “Hz", "value_template": "{{ value_json.frequency}}”,”unique_id": “FREQ”, "device": {"identifiers": [“'+oppleoSystemConfig.chargerID+'_FREQ”], "name": “Frequency” }}'
        self.publish(topic=configTopic, message=FREQ)

        # The active charge session



    def is_connected(self) -> bool:
        return self.homeAssistantMqttClient.is_connected()

    def disconnect(self) -> None:
        HomeAssistantMqttClient.logger.debug("Requesting disconnect from HomeAssistant MQTT Broker...")
        if self.is_connected():
            HomeAssistantMqttClient.logger.debug("Disconnecting from HomeAssistant MQTT Broker...")
            self.homeAssistantMqttClient.disconnect()

    def setUser(self) -> None:
        if oppleoSystemConfig.homeAssistantMqttUsername is not None and oppleoSystemConfig.homeAssistantMqttUsername is not "": 
            HomeAssistantMqttClient.logger.debug("Setting user for HomeAssistant MQTT Broker to {}...".format(oppleoSystemConfig.homeAssistantMqttUsername))
            self.homeAssistantMqttClient.username_pw_set( oppleoSystemConfig.homeAssistantMqttUsername, 
                                                          oppleoSystemConfig.homeAssistantMqttPassword if oppleoSystemConfig.homeAssistantMqttPassword is not None and oppleoSystemConfig.homeAssistantMqttPassword is not "" else None
                                                        )
    

    def publishEnergyDevice(self, A1:float=0, A2:float=0, A3:float=0, V1:float=0, V2:float=0, V3:float=0, E1:float=0, E2:float=0, E3:float=0, ET:float=0, P1:float=0, P2:float=0, P3:float=0, frequency:float=0) -> None:
        global oppleoSystemConfig

        HomeAssistantMqttClient.logger.debug("Sending Energy Device status update messages to HomeAssistant MQTT Broker...")

        stateTopic = 'homeassistant/sensor/'+oppleoSystemConfig.chargerID+'/state'
        message = '{ “A1”: {:.1f}, “A2”: {:.1f}, “A3”: {:.1f}, “V1”: {:.1f}, “V2”: {:.1f}, “V3”: {:.1f}, “E1”: {:.1f}, “E2”: {:.1f}, “E3”: {:.1f}, ET: {:.1f}, “P1”: {:.1f}, “P2”: {:.1f}, “P3”: {:.1f}, “frequency”: {:.1f} }'.format(A1, A2, A3, V1, V2, V3, E1, E2, E3, ET, P1, P2, P3, frequency)
        self.publish(topic=stateTopic, message=message)

    """
        timeout in ms
    """
    def publish(self, topic:str='homeassistant', message:str=None, waitForPublish:bool=False, timeout:int=1000) -> bool:
        HomeAssistantMqttClient.logger.debug(f'Publish msg {message} to HomeAssistant topic {topic} ... ')

        if not self.homeAssistantMqttClient.is_connected():
            HomeAssistantMqttClient.logger.debug("Not connected to HomeAssistant MQTT Broker, trying to connect")
            self.connect()

        # Can be async connected, with self.mqttClient.is_connected() returning false...

        #        if not self.mqttClient.is_connected():
        #            OppleoMqttClient.logger.warn(f'Failed to publish msg {message} to topic {topic}, not connected')
        #            return False
            
        HomeAssistantMqttClient.logger.debug(f'Publishing HomeAssistant MQTT msg {message} to topic {topic}')
        
        try:
            homeAssistantMqttMessageInfo = self.homeAssistantMqttClient.publish(topic=topic, payload=message)
            if waitForPublish:
                homeAssistantMqttMessageInfo.wait_for_publish(timeout=(timeout/1000))
        except (ValueError, TypeError, RuntimeError) as e:
            return False
        return homeAssistantMqttMessageInfo.is_published()
