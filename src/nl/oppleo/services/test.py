import time
from enum import Enum

from nl.oppleo.config.OppleoConfig import oppleoConfig
from nl.oppleo.utils.ModulePresence import modulePresence
from nl.oppleo.utils.EvseReaderUtil import EvseReaderUtil

class EvseDirection(Enum):
    UP = 1
    DOWN = -1
    NONE = 0

GPIO = modulePresence.GPIO

if oppleoConfig.gpioMode == "BOARD":
    print("Setting GPIO MODE to BOARD")
    GPIO.setmode(GPIO.BOARD)
else:
    print("Setting GPIO MODE to BCM")
    GPIO.setmode(GPIO.BCM)

def current_time_milliseconds():
    return time.time() * 1000


def determine_evse_direction(delta):
    delta_int = round(delta)

    direction = EvseDirection.NONE
    if delta_int > 0:
        direction = EvseDirection.UP
    elif delta_int < 0:
        direction = EvseDirection.DOWN

    return direction

EVSE_MINLEVEL_STATE_CONNECTED = 8  # A dc lower than this indicates state A, higher state B

EVSE_MIN_TIME_TO_PULSE = 500  # Min time im ms between rising edges to be pulsing. Faster is ERROR
# Max time it takes to change direction when pulsing. If it's takes longer, assume it's changing it's level
# (ie turned on) and is not pulsing. Value is chosen intuitively.
EVSE_MAX_TIME_TO_PULSE = 4 * EVSE_MIN_TIME_TO_PULSE

SAMPLE_TIME = 0.05  # .05 sec

def is_current_measurement_interval_normal_pulse(evse_measurement_milliseconds):
    '''
    Is duration since evse_measurement_milliseconds the normal time the evse needs to pulse.
    :param evse_measurement_milliseconds:
    :return:
    '''
    delta = current_time_milliseconds() - evse_measurement_milliseconds
    print('Normal pulse cycle? interval of change is calculated: %f' % delta)
    return evse_measurement_milliseconds is not None \
           and (EVSE_MAX_TIME_TO_PULSE > delta >= EVSE_MIN_TIME_TO_PULSE)


def is_current_measurement_interval_error_pulse(evse_measurement_milliseconds):
    '''
    Error pulse goes faster than the normal pulse.
    :param evse_measurement_milliseconds:
    :return:
    '''
    delta = current_time_milliseconds() - evse_measurement_milliseconds
    print('Error pulse cycle? interval of change is calculated: %f' % delta)
    return evse_measurement_milliseconds is not None and (delta < EVSE_MIN_TIME_TO_PULSE)


def is_pulse_direction_changed(direction_current, direction_previous):
    return direction_current != direction_previous



if GPIO is None:
    print("EVSE LED Reader is enabled but GPIO is not loaded (config error).")

    exit

GPIO.setup(oppleoConfig.pinEvseLed, GPIO.IN, pull_up_down=GPIO.PUD_UP)

pigpio_pi = modulePresence.pigpio.pi()

evse_reader = EvseReaderUtil(pigpio=modulePresence.pigpio, pi=pigpio_pi, pin=oppleoConfig.pinEvseLed)
print('Init EvseReaderUtil done')

print('EvseState.EVSE_STATE_UNKNOWN')

"""
if the Duty Cycle is changing, assume it is charging
    detect the speed, is it too high, then it must be an error
if the Duty Cycle is constant, check if it is 10  (CONNECTED), or lower (INACTIVE)

possible required improvements
- CONNECTED when 90 or higher?
- when initially charging starts the freq can be measured as 22k and dc going from 0-2-0-1-1 (5x) -2-3-4 etc
this triggers ERROR state. Place a filter on this.
"""

# Overall direction of the measured pulse. If current measure is equal to previous measure (EvseDirection.NONE)
# the overall direction stays the direction before the direction became NONE. So when the measured value changes
# we can see if it continues the UP or DOWN or switches. Duration of the direction (evse_direction_change_moment)
# is input for us to determine if evse is charging or in error (pulses faster).
evse_direction_overall = None
# Direction of the pulse when we saw the direction of pulse switched (the new direction)
# so together with the evse_direction_overall (current direction, ignoring EvseDirection.NONE measures)
# we can see if the direction switched (and hence means evse is charging or in error).
evse_direction_overall_previous = None
# Current direction of pulse. UP, DOWN or NONE.
evse_direction_current = None
# Contains the moment the direction_overall changes from UP to DOWN or vv.
evse_direction_change_moment = current_time_milliseconds()
# Timestamp since the evse values didn't change anymore (if applicable, otherwise None)
evse_stable_since = None

# Current and previous evse measure. To know if direction of pulse is UP, DOWN or NONE
evse_dcf = None
evse_dcf_prev = None

# When starting pwm the readings might be shirt leading to false positive errors. Filter
error_filter_value = 3
error_filter = error_filter_value

print(" Starting, state is unknown")
while True:

    print("In loop to read evse status")

    time.sleep(SAMPLE_TIME)

    evse_dcf = evse_reader.evse_value()

    # First run?
    if evse_dcf_prev is None:
        evse_dcf_prev = evse_dcf
        continue  # next iteration

    print('determine_evse_direction: evse_dcf={evse_dcf},evse_dcf_prev={evse_dcf_prev}', format(evse_dcf=evse_dcf, evse_dcf_prev=evse_dcf_prev))
    evse_direction_current = determine_evse_direction(evse_dcf - evse_dcf_prev)
    print('evse_direction_current: evse_direction_current={evse_direction_current}', format(evse_direction_current=evse_direction_current))
    if evse_direction_current != EvseDirection.NONE:
        evse_direction_overall = evse_direction_current

    print('evse_current and prev %f vs %f' % (evse_dcf, evse_dcf_prev))
    if evse_direction_current == EvseDirection.NONE:
        print(
            'Direction is neutral. Overall direction %s.' % evse_direction_overall.name if evse_direction_overall else '<null>')
        if evse_stable_since is None:
            evse_stable_since = current_time_milliseconds()

        if is_current_measurement_interval_normal_pulse(evse_stable_since):
            print('In the time-span a pulse would change direction, the evse value did not change')
            if evse_dcf >= EVSE_MINLEVEL_STATE_CONNECTED:
                print("Evse is connected (not charging)")
            else:
                print("Evse is inactive (not charging)")
                # State A (Inactive)