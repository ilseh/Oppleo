import logging
import threading
import time

from nl.carcharging.services.LedLightProdHardware import LedLightProdHardware
from nl.carcharging.utils.GenericUtil import GenericUtil

GenericUtil.importGpio()

PULSE_LED_MIN = 3
PULSE_LED_MAX = 98

# Interval in ms to update led light
FREQ_MS_TO_UPDATE_LED = 10


class LedLightPulseProd(object):

    def __init__(self, color, intensity, pwm=None):
        self.thread_for_pulse = threading.Thread(target=self._pulse)
        self.color = color
        self.logger = logging.getLogger('nl.carcharging.services.LedLightPulseProd')
        self.pwm = pwm
        # For pulse intensity is not used yet.
        self.intensity = intensity
        self.hardware = LedLightProdHardware(self.color)

    # TODO: move to a more generic utility class?
    def millis(self):
        return int(round(time.time() * 1000))

    def _pulse(self):
        pulse_led_value = 0
        pulse_led_millis = 0
        pulse_led_up = True
        self.pwm = self.hardware.init_gpio_pwm()
        try:
            self.pwm.start(0)
            self.logger.debug('Starting led pulse')
            t = threading.currentThread()
            while getattr(t, "do_run", True):
                if self.millis() > (pulse_led_millis + FREQ_MS_TO_UPDATE_LED):
                    if ((pulse_led_up and (pulse_led_value >= PULSE_LED_MAX)) or
                            ((not pulse_led_up) and (pulse_led_value <= PULSE_LED_MIN))):
                        pulse_led_up = not pulse_led_up
                    if pulse_led_up:
                        pulse_led_value += 1
                    else:
                        pulse_led_value -= 1
                    self.pwm.ChangeDutyCycle(pulse_led_value)
                    self.logger.debug("pulseLedValue = ", pulse_led_value)
                    pulse_led_millis = self.millis()
                # Short sleep to fix issue rfid reader was not working anymore. Sleep to free some resource?
                time.sleep(.001)

        except Exception as ex:
            self.logger.error('Exception pulsing %s' % ex)

        finally:
            self._pwm_off()

    def _pwm_off(self):
        self.logger.debug('Stopping led light %s' % self.hardware.color_desc())
        try:
            self.pwm.stop()
        except Exception as ex:
            self.logger.debug("Could not stop pwm, assume not running %s" % ex)

    def cleanup(self):
        self.hardware.cleanup()

    def on(self):
        self.thread_for_pulse = threading.Thread(target=self._pulse)
        self.logger.debug('Attempt to start pulse in thread')
        try:
            self.thread_for_pulse.start()
        except Exception as ex:
            self.logger.warning("Could not start pulsing in thread: %s" % ex)
        self.logger.debug('Pulse started in thread')

    def off(self):
        self.thread_for_pulse.do_run = False
        self.thread_for_pulse.join()
        self.logger.debug('Pulse %s stopped' % self.hardware.color_desc())
