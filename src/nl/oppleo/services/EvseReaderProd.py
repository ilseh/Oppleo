import time
from enum import Enum, IntEnum
import logging

from nl.oppleo.utils.EvseReaderUtil import EvseReaderUtil
from nl.oppleo.utils.GenericUtil import GenericUtil
from nl.oppleo.config.OppleoConfig import OppleoConfig

LOGGER_PATH = "nl.oppleo.services.EvseReaderProd"

oppleoConfig = OppleoConfig()

try:
    import pigpio
except ModuleNotFoundError:
    evseProdLogger = logging.getLogger(LOGGER_PATH)
    evseProdLogger.debug('EvseReaderProd: import pigpio caused ModuleNotFoundError!!!')


GPIO = GenericUtil.importGpio()


class EvseDirection(Enum):
    UP = 1
    DOWN = -1
    NONE = 0

# enum.Enum is not jsonify serializable, IntEnum can be dumped using json.dumps()
class EvseState(IntEnum):
    EVSE_STATE_UNKNOWN = 0  # Initial
    EVSE_STATE_INACTIVE = 1  # SmartEVSE State A: LED ON dimmed. Contactor OFF. Inactive
    EVSE_STATE_CONNECTED = 2  # SmartEVSE State B: LED ON full brightness, Car connected
    EVSE_STATE_CHARGING = 3  # SmartEVSE State C: charging (pulsing)
    EVSE_STATE_ERROR = 4  # SmartEVSE State ?: ERROR (quick pulse)


EVSE_MINLEVEL_STATE_CONNECTED = 8  # A dc lower than this indicates state A, higher state B

EVSE_MIN_TIME_TO_PULSE = 500  # Min time im ms between rising edges to be pulsing. Faster is ERROR
# Max time it takes to change direction when pulsing. If it's takes longer, assume it's changing it's level
# (ie turned on) and is not pulsing. Value is chosen intuitively.
EVSE_MAX_TIME_TO_PULSE = 4 * EVSE_MIN_TIME_TO_PULSE

SAMPLE_TIME = 0.05  # .05 sec


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


def is_current_measurement_interval_normal_pulse(evse_measurement_milliseconds):
    '''
    Is duration since evse_measurement_milliseconds the normal time the evse needs to pulse.
    :param evse_measurement_milliseconds:
    :return:
    '''
    logger = logging.getLogger(LOGGER_PATH)
    delta = current_time_milliseconds() - evse_measurement_milliseconds
    logger.debug('Normal pulse cycle? interval of change is calculated: %f' % delta)
    return evse_measurement_milliseconds is not None \
           and (EVSE_MAX_TIME_TO_PULSE > delta >= EVSE_MIN_TIME_TO_PULSE)


def is_current_measurement_interval_error_pulse(evse_measurement_milliseconds):
    '''
    Error pulse goes faster than the normal pulse.
    :param evse_measurement_milliseconds:
    :return:
    '''
    logger = logging.getLogger(LOGGER_PATH)
    delta = current_time_milliseconds() - evse_measurement_milliseconds
    logger.debug('Error pulse cycle? interval of change is calculated: %f' % delta)
    return evse_measurement_milliseconds is not None and (delta < EVSE_MIN_TIME_TO_PULSE)


def is_pulse_direction_changed(direction_current, direction_previous):
    return direction_current != direction_previous


class EvseReaderProd:

    def __init__(self):
        self.logger = logging.getLogger(LOGGER_PATH)
        self.logger.setLevel(logging.WARNING)

    def loop(self, cb_until, cb_result):
        global oppleoConfig

        self.logger.debug('In loop, doing setup GPIO')
        # set GPIO mode globally (to BCM)
        # GPIO.setmode(GPIO.BCM)  # BCM / GIO mode

        if GPIO is None:
            self.logger.warn("EVSE LED Reader is enabled but GPIO is not loaded (config error).")
            cb_result(EvseState.EVSE_STATE_UNKNOWN)
            while not cb_until():
                # Loop here untill done
                oppleoConfig.appSocketIO.sleep(1)
            return

        GPIO.setup(oppleoConfig.pinEvseLed, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        pigpio_pi = pigpio.pi()

        evse_reader = EvseReaderUtil(pigpio_pi, oppleoConfig.pinEvseLed)
        self.logger.debug('Init EvseReaderUtil done')

        evse_state = EvseState.EVSE_STATE_UNKNOWN  # active state INACTIVE | CONNECTED | CHARGING | ERROR

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

        self.logger.info(" Starting, state is {}".format(evse_state.name))
        while not cb_until():

            self.logger.debug("In loop to read evse status")

            oppleoConfig.appSocketIO.sleep(SAMPLE_TIME)

            evse_dcf = evse_reader.evse_value()

            # First run?
            if evse_dcf_prev is None:
                evse_dcf_prev = evse_dcf
                continue  # next iteration

            evse_direction_current = determine_evse_direction(evse_dcf - evse_dcf_prev)
            if evse_direction_current != EvseDirection.NONE:
                evse_direction_overall = evse_direction_current

            self.logger.debug('evse_current and prev %f vs %f' % (evse_dcf, evse_dcf_prev))
            if evse_direction_current == EvseDirection.NONE:
                self.logger.debug(
                    'Direction is neutral. Overall direction %s.' % evse_direction_overall.name if evse_direction_overall else '<null>')
                if evse_stable_since is None:
                    evse_stable_since = current_time_milliseconds()

                if is_current_measurement_interval_normal_pulse(evse_stable_since):
                    self.logger.debug('In the time-span a pulse would change direction, the evse value did not change')
                    if evse_dcf >= EVSE_MINLEVEL_STATE_CONNECTED:
                        self.logger.debug("Evse is connected (not charging)")
                        evse_state = EvseState.EVSE_STATE_CONNECTED
                    else:
                        self.logger.debug("Evse is inactive (not charging)")
                        # State A (Inactive)
                        evse_state = EvseState.EVSE_STATE_INACTIVE
                # Connected or Inactive - reset error filter
                error_filter = error_filter_value
            else:
                # Evse measure changed
                evse_stable_since = None
                if is_pulse_direction_changed(evse_direction_overall, evse_direction_overall_previous):
                    self.logger.debug(
                        'Direction of evse dutycycle changed. Current direction overall: %s' % evse_direction_overall.name)
                    if is_current_measurement_interval_normal_pulse(evse_direction_change_moment):
                        evse_state = EvseState.EVSE_STATE_CHARGING
                        # Charging - reset error filter
                        error_filter = error_filter_value
                    elif is_current_measurement_interval_error_pulse(evse_direction_change_moment):
                        if error_filter == 0:
                            evse_state = EvseState.EVSE_STATE_ERROR
                        else:
                            error_filter -= 1
                    else:
                        self.logger.debug('Changed direction too slow, is not pulsing, assume only level changed.')
                        # Charging - reset error filter
                        error_filter = error_filter_value
                    evse_direction_overall_previous = evse_direction_overall
                    evse_direction_change_moment = current_time_milliseconds()

            self.logger.debug("Current evse_state %s" % evse_state.name)
            cb_result(evse_state)
            # Remember current evse direction for next run
            evse_direction_previous = evse_direction_overall
            # Remember current duty cycle for next run
            evse_dcf_prev = evse_dcf

        evse_reader.cancel()

        pigpio_pi.stop()

