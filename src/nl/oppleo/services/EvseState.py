
from enum import IntEnum

# enum.Enum is not jsonify serializable, IntEnum can be dumped using json.dumps()
class EvseState(IntEnum):
    EVSE_STATE_UNKNOWN = 0  # Initial
    EVSE_STATE_INACTIVE = 1  # SmartEVSE State A: LED ON dimmed. Contactor OFF. Inactive
    EVSE_STATE_CONNECTED = 2  # SmartEVSE State B: LED ON full brightness, Car connected
    EVSE_STATE_CHARGING = 3  # SmartEVSE State C: charging (pulsing)
    EVSE_STATE_ERROR = 4  # SmartEVSE State ?: ERROR (quick pulse)

def EvseStateName(evse_state:EvseState=EvseState.EVSE_STATE_UNKNOWN):
    if evse_state == EvseState.EVSE_STATE_INACTIVE:
        return 'Inactive'
    if evse_state == EvseState.EVSE_STATE_CONNECTED:
        return 'Connected'
    if evse_state == EvseState.EVSE_STATE_CHARGING:
        return 'Charging'
    if evse_state == EvseState.EVSE_STATE_ERROR:
        return 'ERROR'
    # if evse_state == EvseState.EVSE_STATE_UNKNOWN:
    return 'Unknown'
