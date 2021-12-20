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


class OppleoMqttClient(object, metaclass=Singleton):
    logger = logging.getLogger('nl.oppleo.services.OppleoMqttClient')
    mqttClient = None

    def __init__(self) -> None:
        super().__init__()
        # Set Connecting Client ID
        self.mqttClient = mqtt_client.Client(client_id='Oppleo_'+oppleoSystemConfig.chargerName, 
                                             clean_session=True,
                                             protocol=MQTTv311,
                                             transport="tcp",
                                             reconnect_on_failure=True
                                             )
        self.setUser()


    def connect(self) -> None:
        OppleoMqttClient.logger.debug("Cconnecting to MQTT Broker...")
        self.mqttClient.connect(host=oppleoSystemConfig.mqttHost, port=oppleoSystemConfig.mqttPort)
        self.mqttClient.loop_start()

    def is_connected(self) -> bool:
        return self.mqttClient.is_connected()

    def disconnect(self) -> None:
        OppleoMqttClient.logger.debug("Requesting disconnect from MQTT Broker...")
        if self.is_connected():
            OppleoMqttClient.logger.debug("Disconnecting from MQTT Broker...")
            self.mqttClient.disconnect()

    def setUser(self) -> None:
        if oppleoSystemConfig.mqttUsername is not None and oppleoSystemConfig.mqttUsername is not "": 
            OppleoMqttClient.logger.debug("Setting user for MQTT Broker to {}...".format(oppleoSystemConfig.mqttUsername))
            self.mqttClient.username_pw_set( oppleoSystemConfig.mqttUsername, 
                                             oppleoSystemConfig.mqttPassword if oppleoSystemConfig.mqttPassword is not None and oppleoSystemConfig.mqttPassword is not "" else None
                                           )
    """
        timeout in ms
    """
    def publish(self, topic:str='oppleo', message:str=None, waitForPublish:bool=False, timeout:int=1000) -> bool:
        OppleoMqttClient.logger.debug(f'Publish msg {message} to topic {topic} ... ')

        if not self.mqttClient.is_connected():
            OppleoMqttClient.logger.debug("Not connected to MQTT Broker, trying to connect")
            self.connect()

        # Can be async connected, with self.mqttClient.is_connected() returning false...

        #        if not self.mqttClient.is_connected():
        #            OppleoMqttClient.logger.warn(f'Failed to publish msg {message} to topic {topic}, not connected')
        #            return False
            
        OppleoMqttClient.logger.debug(f'Publishing MQTT msg {message} to topic {topic}')
        
        try:
            mqttMessageInfo = self.mqttClient.publish(topic=topic, payload=message)
            if waitForPublish:
                mqttMessageInfo.wait_for_publish(timeout=(timeout/1000))
        except (ValueError, TypeError, RuntimeError) as e:
            return False
        return mqttMessageInfo.is_published()
