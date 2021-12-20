import logging
from nl.oppleo.config.OppleoSystemConfig import OppleoSystemConfig

from paho.mqtt import client as mqtt_client #, MQTTMessageInfo

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
    connected = False

    def __init__(self) -> None:
        super().__init__()
        # Set Connecting Client ID
        self.mqttClient = mqtt_client.Client('Oppleo_'+oppleoSystemConfig.chargerName)
        self.setUser()
        # Connect callback
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                OppleoMqttClient.logger.debug("Connected to MQTT Broker")
                self.connected = True
            else:
                OppleoMqttClient.logger.warn("Failed to connect to MQTT Broker! Return code {}".format(rc))
                self.connected = False
        # Disconnect callback
        def on_disconnect(client, userdata, flags, rc):
            OppleoMqttClient.logger.warn("Disconnected from MQTT Broker ({})".format(rc))
            self.connected = False
        self.mqttClient.on_connect = on_connect
        self.mqttClient.on_disconnect = on_disconnect


    def connect(self) -> None:
        OppleoMqttClient.logger.debug("Cconnecting to MQTT Broker...")
        self.mqttClient.connect(oppleoSystemConfig.mqttHost, oppleoSystemConfig.mqttPort)


    def disconnect(self) -> None:
        OppleoMqttClient.logger.debug("Disconnecting from MQTT Broker...")
        self.mqttClient.disconnect()


    def setUser(self) -> None:
        if oppleoSystemConfig.mqttUsername is not None and oppleoSystemConfig.mqttUsername is not "": 
            OppleoMqttClient.logger.debug("Setting user for MQTT Broker to {}...".format(oppleoSystemConfig.mqttUsername))
            self.mqttClient.username_pw_set( oppleoSystemConfig.mqttUsername, 
                                             oppleoSystemConfig.mqttPassword if oppleoSystemConfig.mqttPassword is not None and oppleoSystemConfig.mqttPassword is not "" else None
                                           )


    def publish(self, topic, message) -> bool:
        OppleoMqttClient.logger.debug(f'Publish msg {message} to topic {topic} ... ')

        if not self.connected or self.mqttClient is None:
            OppleoMqttClient.logger.debug("Not connected to MQTT Broker, trying to connect")
            self.connect()
        if not self.connected or self.mqttClient is None:
            OppleoMqttClient.logger.warn(f'Failed to publish msg {message} to topic {topic}, not connected')
            return
            
        OppleoMqttClient.logger.debug(f'Publishing MQTT msg {message} to topic {topic}')
        mqttMessageInfo = self.mqttClient.publish(topic, message)
        return mqttMessageInfo.rc == 2 #MQTTMessageInfo.MQTT_ERR_SUCCESS
