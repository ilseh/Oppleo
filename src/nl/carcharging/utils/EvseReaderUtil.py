import enum
import logging

from nl.carcharging.config import Logger

import pigpio


class EvseReaderUtil:
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

        self._new_weighting = 1.0 - weighting  # Weighting for new reading.
        self._old_weighting = weighting  # Weighting for old reading.

        self._high_tick = None
        self._pwm_frequency = None
        self._pwm_pulse_width_microseconds = None

        self._cb = pi.callback(gpio, pigpio.EITHER_EDGE, self._cbf)

    def _cbf(self, gpio, level, tick):

        # 1 = change to high (a rising edge)
        if level == 1:
            self._pwm_frequency = self._do_something_with_pulse(self._pwm_frequency, tick)
            self._high_tick = tick

        # 0 = change to low (a falling edge)
        elif level == 0:
            self._pwm_pulse_width_microseconds = self._do_something_with_pulse(self._pwm_pulse_width_microseconds, tick)

    def _do_something_with_pulse(self, old_value_of_interest, tick):
        new_value_of_interest = old_value_of_interest
        if self._high_tick is not None:
            t = pigpio.tickDiff(self._high_tick, tick)

            if old_value_of_interest is not None and self._old_weighting is not None and self._new_weighting is not None:
                new_value_of_interest = (self._old_weighting * old_value_of_interest) + (self._new_weighting * t)
            else:
                new_value_of_interest = t
        return new_value_of_interest

    def frequency(self):
        """
      Returns the PWM frequency.
      """
        if self._pwm_frequency is not None:
            return 1000000.0 / self._pwm_frequency
        else:
            return 0.0

    def pulse_width(self):
        """
      Returns the PWM pulse width in microseconds.
      """
        if self._pwm_pulse_width_microseconds is not None:
            return self._pwm_pulse_width_microseconds
        else:
            return 0.0

    def duty_cycle_percentage(self):
        """
      Returns the PWM duty cycle percentage.
      """
        if self._pwm_pulse_width_microseconds is not None and self._pwm_frequency is not None:
            return 100.0 * self._pwm_pulse_width_microseconds / self._pwm_frequency
        else:
            return 0.0

    def evse_value(self):
        '''
        Returns the duty_cycle_percentage but 1-100 is mapped to 1-10
        :return: duty-cycle_percentage/10 (int)
        '''
        return round(self.duty_cycle_percentage() / 10)

    def cancel(self):
        """
      Cancels the reader and releases resources.
      """
        self._cb.cancel()
