#!/usr/bin/env python

class reader:
    """
    A class to read PWM pulses and calculate their frequency
    and duty cycle.  The frequency is how often the pulse
    happens per second.  The duty cycle is the percentage of
    pulse high time per cycle.
    """
    def __init__(self, pi, gpio, weighting=0.0):
        """
        Instantiate with the Pi and gpio of the PWM signal
        to monitor.

        Optionally a weighting may be specified.  This is a number
        between 0 and 1 and indicates how much the old reading
        affects the new reading.  It defaults to 0 which means
        the old reading has no effect.  This may be used to
        smooth the data.
        """
        self.pi = pi
        self.gpio = gpio

        if weighting < 0.0:
            weighting = 0.0
        elif weighting > 0.99:
            weighting = 0.99

        self._new = 1.0 - weighting # Weighting for new reading.
        self._old = weighting       # Weighting for old reading.

        self._high_tick = None
        self._period = None
        self._high = None

        self._cb = pi.callback(gpio, pigpio.EITHER_EDGE, self._cbf)

    def _cbf(self, gpio, level, tick):

        if level == 1:

            if self._high_tick is not None:
                t = pigpio.tickDiff(self._high_tick, tick)

                if self._period is not None and self._old is not None and self._new is not None:
                    self._period = (self._old * self._period) + (self._new * t)
                else:
                    self._period = t

            self._high_tick = tick

        elif level == 0:

            if self._high_tick is not None:
                t = pigpio.tickDiff(self._high_tick, tick)

                if self._high is not None and self._old is not None and self._new is not None:
                    self._high = (self._old * self._high) + (self._new * t)
                else:
                    self._high = t

    def frequency(self):
        """
        Returns the PWM frequency.
        """
        if self._period is not None:
            return 1000000.0 / self._period
        else:
            return 0.0

    def pulse_width(self):
        """
        Returns the PWM pulse width in microseconds.
        """
        if self._high is not None:
            return self._high
        else:
            return 0.0

    def duty_cycle(self):
        """
        Returns the PWM duty cycle percentage.
        """
        if self._high is not None and self._period is not None:
            return 100.0 * self._high / self._period
        else:
            return 0.0

    def cancel(self):
        """
        Cancels the reader and releases resources.
        """
        self._cb.cancel()

EVSE_STATE_UNKNOWN   = 0            # Initial
EVSE_STATE_INACTIVE  = 1            # SmartEVSE State A: LED ON dimmed. Contactor OFF. Inactive
EVSE_STATE_CONNECTED = 2            # SmartEVSE State B: LED ON full brightness, Car connected
EVSE_STATE_CHARGING  = 3            # SmartEVSE State C: charging (pulsing)
EVSE_STATE_ERROR     = 4            # SmartEVSE State ?: ERROR (quick pulse)

EVSE_MINLEVEL_STATE_CONNECTED = 8   # A dc lower than this indicates state A, higher state B

def stateStr(state=EVSE_STATE_UNKNOWN):
    if (state == EVSE_STATE_INACTIVE):
        return "Inactive"
    if (state == EVSE_STATE_CONNECTED):
        return "Connected"
    if (state == EVSE_STATE_CHARGING):
        return "Charging"
    if (state == EVSE_STATE_ERROR):
        return "ERROR"
    return "Unknown"


if __name__ == "__main__":

    import time
    import pigpio
    #   import read_PWM

    PWM_GPIO = 6 	# 4
    RUN_TIME = 3600.0
    SAMPLE_TIME = 0.05	# .05 sec

    g.setmode(g.BCM)        # BCM / GIO mode
    g.setup(6, g.IN, pull_up_down=g.PUD_UP)

    pi = pigpio.pi()

    p = reader(pi, PWM_GPIO)

    start = time.time()

    # -- Duty Cycle filtered
    evse_dcf_prev = None
    evse_changing = None
    evse_rising = None
    evse_rising_since = None
    evse_dcf_lastchange  = None         # time.time() *1000 # now, in ms

    evse_state = EVSE_STATE_UNKNOWN     # active state INACTIVE | CONNECTED | CHARGING | ERROR

    EVSE_TIME_TO_SWITCH_EDGES = 500     # Time a dcf can be steady while pulsing in ms
    EVSE_TIME_TO_PULSE        = 500     # Min time between rising edges to be pulsing. Faster is ERROR

    """
      if the Duty Cycle is changing, assume it is charging
         detect the speed, is it too high, then it must be an error
      if the Duty Cycle is constant, check if it is 10  (CONNECTED), or lower (INACTIVE)
 
      possible required improvements
      - CONNECTED when 90 or higher?
      - when initially charging starts the freq can be measured as 22k and dc going from 0-2-0-1-1 (5x) -2-3-4 etc
        this triggers ERROR state. Place a filter on this.
    """

    debug = 1

    print(" Starting, state is {}".format(stateStr(evse_state)))
    while (time.time() - start) < RUN_TIME:

        time.sleep(SAMPLE_TIME)

        f = p.frequency()
        pw = p.pulse_width()
        dc = p.duty_cycle()
        evse_dcf = round( dc / 10 ) # duty cycle filtered [0-10]

        # first run
        if (evse_dcf_prev == None):
            evse_dcf_prev = evse_dcf
            if debug >= 2: print(" First run...")
            continue # next iteration


        if (evse_dcf == evse_dcf_prev):
            if debug >= 3: print(" 1: evse_dcf == evse_dcf_prev ({})".format(evse_dcf))
            # possible state A, B or just a top/bottom  of a pulse
            # is this the first occurrance?
            if ((evse_changing == None) or evse_changing == True):
                # First time, was changing before
                if debug >= 3: print(" 2: First time, was changing before ({})".format(evse_changing))
                evse_changing = False
                evse_dcf_lastchange  = time.time() *1000 # now, in ms
            if (evse_dcf_lastchange is not None and (((time.time() *1000) - evse_dcf_lastchange) > EVSE_TIME_TO_SWITCH_EDGES)):
                if debug >= 3: print(" 3: time (((time.time() *1000) - evse_dcf_lastchange) > EVSE_TIME_TO_SWITCH_EDGES) {} {}".format(int((time.time() *1000) - evse_dcf_lastchange), EVSE_TIME_TO_SWITCH_EDGES))
                # this condition has been a while, must be state A or B
                if ( evse_dcf >= EVSE_MINLEVEL_STATE_CONNECTED):
                    # State B (Connected)
                    if debug >= 3: print(" 4: Connected")
                    evse_rising = False
                    evse_rising_since = None
                    if (evse_state != EVSE_STATE_CONNECTED):
                        evse_state = EVSE_STATE_CONNECTED
                        # Changing to  Connected
                        if debug >= 1: print(" State changed to {} (dc={})".format(stateStr(evse_state), evse_dcf))
                else:
                    # State A (Inactive)
                    if debug >= 3: print(" 5: Inactive")
                    if (evse_state != EVSE_STATE_INACTIVE):
                        # Changing to  Inactive
                        evse_state = EVSE_STATE_INACTIVE
                        if debug >= 1: print(" State changed to {} (dc={})".format(stateStr(evse_state), evse_dcf))

        if (evse_dcf != evse_dcf_prev):
            if debug >= 3: print(" 6: evse_dcf != evse_dcf_prev ({} {})".format(evse_dcf, evse_dcf_prev))
            # Changing
            if ( evse_dcf > evse_dcf_prev):
                if debug >= 3: print(" 7: evse_dcf larger")
                # rising
                if (evse_rising == None): # starting up
                    if debug >= 3: print(" 8: rising was None, starting up")
                    evse_rising = True
                    evse_rising_since  = time.time() *1000 # now, in ms
                else:
                    if (not evse_rising):     # switching from falling
                        if debug >= 3: print(" 9: switching from falling to rising")
                        evse_rising = True
                        if (not evse_rising_since == None):
                            if debug >= 3: print(" 10: rising since {} now {}".format(evse_rising_since, (time.time() *1000)))
                            # switching to rising, quickly? (can this be ERROR?)
                            if (evse_rising_since is not None and  (((time.time() *1000) - evse_rising_since) < EVSE_TIME_TO_PULSE)):
                                if debug >= 3: print(" 11: very quick - ERROR")
                                # ERROR
                                if (evse_state != EVSE_STATE_ERROR):
                                    evse_state = EVSE_STATE_ERROR
                                    # Changing to ERROR
                                    if debug >= 1: print(" State changed to {}".format(stateStr(evse_state)))
                        evse_rising_since  = time.time() *1000 # now, in ms
                    else:                     # continue rising
                        if debug >= 3: print(" 12: continue rising")
                        if debug >= 3: print(" 13: time (((time.time() *1000) - evse_rising_since) >= EVSE_TIME_TO_PULSE) {} {} ".format(int((time.time() *1000) - evse_rising_since), EVSE_TIME_TO_PULSE))
                        if (evse_rising_since is not None and (((time.time() *1000) - evse_rising_since) >= EVSE_TIME_TO_PULSE)):
                            # Pulse state (Charging)
                            if (evse_state != EVSE_STATE_CHARGING):
                                evse_state = EVSE_STATE_CHARGING
                                # Changing to Charging
                                if debug >= 1: print(" State changed to {}".format(stateStr(evse_state)))
            else:
                # falling
                if debug >= 3: print(" 14: falling")
                if debug >= 3: print(" 15: time (((time.time() *1000) - evse_rising_since) >= EVSE_TIME_TO_PULSE) {} {} ".format(int((time.time() *1000) - evse_rising_since), EVSE_TIME_TO_PULSE))
                if (evse_rising_since is not None and (((time.time() *1000) - evse_rising_since) >= EVSE_TIME_TO_PULSE)):
                    # Pulse state (Charging)
                    if (evse_state != EVSE_STATE_CHARGING):
                        evse_state = EVSE_STATE_CHARGING
                        # Changing to Charging
                        if debug >= 1: print(" State changed to {}".format(stateStr(evse_state)))

                evse_rising = False
            # dcf has changed
            evse_dcf_lastchange = time.time() *1000 # now, in ms
        # Remember current duty cycle for next run
        evse_dcf_prev = evse_dcf

        """
        if ( ( not dc_increasing ) and ( dc > dc_prev ) ):
           # gettin' larger - becoming increasing
           print(" dc decreased for {}ms - now starting increasing ".format(int((time.time()*1000)-dc_increasing_or_decreasing_since)))
           dc_increasing = True
           dc_increasing_or_decreasing_since = time.time() *1000
  
        if ( ( dc_increasing ) and ( dc < dc_prev ) ):
           # gettin' smaller - becomming decreasing
           print(" dc increased for {}ms - now starting decreasing".format(int((time.time()*1000)-dc_increasing_or_decreasing_since)))
           dc_increasing = False
           dc_increasing_or_decreasing_since = time.time() *1000
  
        """
        if debug >= 2: print("f={:.1f} pw={} dc={:.2f} dcf={}".format(f, int(pw+0.5), dc, evse_dcf))


        #print(" {:.1f} {}".format(time.time(), int(round(time.time() * 1000)))

    #      if ( pw_increasing ):
    #         print(" pw increasing since {} (already {}ms)".format(pw_increasing_or_decreasing_since, int((time.time()*1000)-pw_increasing_or_decreasing_since)))
    #      else:
    #         print(" pw decreasing since {} (already {}ms)".format(pw_increasing_or_decreasing_since, int((time.time()*1000)-pw_increasing_or_decreasing_since)))

    p.cancel()

    pi.stop()


