
"""
 WebSocket
    namespace       bijv. /evse_status
    wsEmitQueue     oppleoConfig.wsEmitQueue,
    event           bijv.  evse_enabled, update, charge_session_started, charge_session_ended, charge_session_status_update
    id              oppleoConfig.chargerID,
    public          True is niet ingelogd
    data            bericht
    room            prive bericht

                      wsEmitQueue=oppleoConfig.wsEmitQueue,
                            event='charge_session_status_update', 
                            status=evse_state, 
                            id=oppleoConfig.chargerID, 
                            namespace='/charge_session',
                            public=True


 MQTT
    topic: oppleo/{oppleoConfig.chargerID}/namespace/event
    message: data 
    - ignore public
    - status?


"""


     
import logging
import json
from nl.oppleo.config.OppleoSystemConfig import OppleoSystemConfig
from nl.oppleo.config.OppleoConfig import OppleoConfig
from nl.oppleo.services.OppleoMqttClient import OppleoMqttClient

oppleoSystemConfig = OppleoSystemConfig()
oppleoConfig = OppleoConfig()


class OutboundEvent(object):
    logger = logging.getLogger('nl.oppleo.utils.OutboundEvent')

    """ 
      public = When True emits the message and contents to all connected clients. When False only emits to 
               authenticated clients
    """ 
    @staticmethod
    def triggerEvent( event='event',         \
                      data=None,             \
                      status=None,           \
                      id=None,               \
                      namespace=None,        \
                      public=False,          \
                      room=None):

        # Send websocket event (always enabled)
        OutboundEvent.emitWebsocketEvent( wsEmitQueue=oppleoConfig.wsEmitQueue,     \
                                          event=event,                              \
                                          data=data,                                \
                                          status=status,                            \
                                          id=id,                                    \
                                          namespace=namespace,                      \
                                          public=public,                            \
                                          room=room)

        # Send MQTT event if enabled
        if oppleoSystemConfig.mqttOutboundEnabled and room is not None:
            OutboundEvent.logger.debug('Webclient specific message (system status on connect) not send to MQTT.')
        if oppleoSystemConfig.mqttOutboundEnabled and room is None:
            OutboundEvent.emitMQTTEvent( event=event,                               \
                                         data=data,                                 \
                                         status=status,                             \
                                         id=id,                                     \
                                         namespace=namespace)


    """ 

    """ 
    @staticmethod
    def emitMQTTEvent( event='event',
                       data=None,
                       status=None,
                       id=None,
                       namespace='/all',
                       waitForPublish=False):

        oppleoMqttClient = OppleoMqttClient()

        topic = 'oppleo/' + oppleoSystemConfig.chargerID + namespace + '/' + event

        msg = {}
        if data is not None:
            msg['data'] = data
        if id is not None:
            msg['id'] = id
        if status is not None:
            msg['status'] = status

        OutboundEvent.logger.debug(f'Submit msg to MQTT topic ... {msg}')
        try:
            oppleoMqttClient.publish(topic=topic, message=json.dumps(msg, default=str), waitForPublish=waitForPublish)
        except Exception as e:
            OutboundEvent.logger.error('MQTT server enabled but not reachable! {}'.format(str(e)))



    """ 
      public    = When True emits the message and contents to all connected clients. When False only emits to 
                  authenticated clients
      room      = specific web client (on connect), no other rooms used 
    """ 
    @staticmethod
    def emitWebsocketEvent( wsEmitQueue=oppleoConfig.wsEmitQueue,   \
                            event='event',         \
                            data=None,             \
                            status=None,           \
                            id=None,               \
                            namespace=None,        \
                            public=False,          \
                            room=None):

        if wsEmitQueue is not None:
            msg = {}
            msg['event'] = event
            """
            while 'data' in data:
                # Nested, unravel
                data = data['data']
            """
            if data is not None:
                msg['data'] = data
            if status is not None:
                msg['status'] = status
            if id is not None:
                msg['id'] = id
            if room is not None:
                msg['room'] = room
            msg['namespace'] = namespace
            msg['public'] = public
            OutboundEvent.logger.debug(f'Submit msg to websocket emit queue ... {msg}')
            wsEmitQueue.put(msg)
        else:
            OutboundEvent.logger.debug('Websocket emit queue not instantiated')
