
import logging
from datetime import datetime
import json

from nl.oppleo.config.OppleoSystemConfig import OppleoSystemConfig
from nl.oppleo.config.OppleoConfig import OppleoConfig
from nl.oppleo.services.EvseState import EvseState, EvseStateName
from nl.oppleo.utils.ModulePresence import modulePresence
from nl.oppleo.models.ChargeSessionModel import ChargeSessionModel

oppleoSystemConfig = OppleoSystemConfig()
oppleoConfig = OppleoConfig()

"""
    If no charge session is active - EVSE_STATE_INACTIVE
    If charge session is active
    Minutes:
    - Every 0/3/6/8th minute the state is EVSE_STATE_CONNECTED
    - Every 1/2/4/5/7/9th minute the state is EVSE_STATE_CHARGING
        [0] EVSE_STATE_CONNECTED
        [1] EVSE_STATE_CHARGING
        [2] EVSE_STATE_CHARGING
        [3] EVSE_STATE_CONNECTED
        [4] EVSE_STATE_CHARGING
        [5] EVSE_STATE_CHARGING
        [6] EVSE_STATE_CONNECTED
        [7] EVSE_STATE_CHARGING
        [8] EVSE_STATE_CONNECTED
        [9] EVSE_STATE_CHARGING

    EVSE_STATE_UNKNOWN = 0      # Initial
    EVSE_STATE_INACTIVE = 1     # SmartEVSE State A: LED ON dimmed. Contactor OFF. Inactive
    EVSE_STATE_CONNECTED = 2    # SmartEVSE State B: LED ON full brightness, Car connected
    EVSE_STATE_CHARGING = 3     # SmartEVSE State C: charging (pulsing)
    EVSE_STATE_ERROR = 4        # SmartEVSE State ?: ERROR (quick pulse)

"""


class EvseReaderSimulate(object):
    __logger = None
    __current_state = None    
    __openSession = None    

    def __init__(self):
        self.__logger = logging.getLogger(self.__class__.__module__)
        self.__logger.setLevel(level=oppleoSystemConfig.getLogLevelForModule(self.__class__.__module__))   
        self.__current_state = EvseState.EVSE_STATE_UNKNOWN

    def loop(self, cb_until, cb_result):
        global oppleoConfig

        cb_result(EvseState.EVSE_STATE_UNKNOWN)
        self.__logger.warn('Simulated Evse Read loop!')
        while not cb_until():

            self.__openSession = ChargeSessionModel.getOpenChargeSession(oppleoConfig.chargerID)

            if self.__openSession is None and self.__current_state != EvseState.EVSE_STATE_INACTIVE:
                self.__logger.warn('SIMULATE EVSE state change to INACTIVE!')
                self.__current_state = EvseState.EVSE_STATE_INACTIVE
                cb_result(EvseState.EVSE_STATE_INACTIVE)

            if self.__openSession is not None:

                minute = datetime.now().minute % 9
                self.__logger.debug('Simulated Evse Read loop!')

                if minute in [0, 3, 6, 8] and self.__current_state != EvseState.EVSE_STATE_CONNECTED:
                    self.__logger.warn('SIMULATE EVSE state change to CONNECTED!')
                    self.__current_state = EvseState.EVSE_STATE_CONNECTED
                    cb_result(EvseState.EVSE_STATE_CONNECTED)
                if minute in [1, 2, 4, 5, 7, 9] and self.__current_state != EvseState.EVSE_STATE_CHARGING:
                    self.__logger.warn('SIMULATE EVSE state change to CHARGING!')
                    self.__current_state = EvseState.EVSE_STATE_CHARGING
                    cb_result(EvseState.EVSE_STATE_CHARGING)

            oppleoConfig.appSocketIO.sleep(2)


    def diag(self):
        return json.dumps({
            "__current_state": EvseStateName(evse_state=self.__current_state),
            "__openSession": "None" if self.__openSession is None else json.loads(self.__openSession.to_json())
            }, 
            default=str     # Overcome "TypeError: Object of type datetime is not JSON serializable"
        )

        return json.dumps({
            "__current_state": EvseStateName(evse_state=self.__current_state),
            "__openSession": "None" if self.__openSession is None else self.__openSession.to_json()
            }, 
            default=str     # Overcome "TypeError: Object of type datetime is not JSON serializable"
        )
