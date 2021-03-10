import logging
import threading
import time

from nl.oppleo.config.OppleoConfig import OppleoConfig
from nl.oppleo.services.LedPinDefinition import LedPinDefinition
from nl.oppleo.services.LedLightProdHardware import LedLightProdHardware

oppleoConfig = OppleoConfig()

# Interval in ms to update led light
FREQ_MS_TO_UPDATE_LED = 10

class LedLightPulseProd(object):
    __logger = None
    __thread_for_pulse = None
    __pinDefinition:LedPinDefinition = 0
    colorName = "Unknown"
    pwm = None
    intensity = 0
    hardware = None

    def __init__(self, pinDefinition:LedPinDefinition, intensity:int=0, pwm=None):
        self.__logger = logging.getLogger('nl.oppleo.services.LedLightPulseProd')
        self.__thread_for_pulse = threading.Thread(target=self._pulse, name="LedPulseThread")
        self.__pinDefinition = pinDefinition
        self.pwm = pwm
        # For pulse intensity is not used yet.
        self.intensity = intensity
        self.hardware = LedLightProdHardware(pinDefinition=pinDefinition)

    def millis(self):
        return int(round(time.time() * 1000))

    def _pulse(self):
        global oppleoConfig

        pulse_led_value = 0
        pulse_led_millis = 0
        pulse_led_up = True
        self.pwm = self.hardware.init_gpio_pwm()
        try:
            self.pwm.start(0)
            self.__logger.debug('LedLightPulseProd._pulse() - Starting led pulse')
            t = threading.currentThread()
            while getattr(t, "do_run", True):
                if self.millis() > (pulse_led_millis + FREQ_MS_TO_UPDATE_LED):
                    if ((pulse_led_up and (pulse_led_value >= oppleoConfig.pulseLedMax)) or
                            ((not pulse_led_up) and (pulse_led_value <= oppleoConfig.pulseLedMin))):
                        pulse_led_up = not pulse_led_up
                    if pulse_led_up:
                        pulse_led_value += 1
                    else:
                        pulse_led_value -= 1
                    self.pwm.ChangeDutyCycle(pulse_led_value)
                    self.__logger.debug("LedLightPulseProd._pulse() - pulseLedValue = {}".format(str(pulse_led_value)))
                    pulse_led_millis = self.millis()
                # Short sleep to fix issue rfid reader was not working anymore. Sleep to free some resource?
                time.sleep(.001)

        except Exception as e:
            self.__logger.error('LedLightPulseProd._pulse() - Exception pulsing {}'.format(str(e)))

        finally:
            self._pwm_off()

    def _pwm_off(self):
        self.__logger.debug('LedLightPulseProd._pwm_off() - Stopping led light {} (intensity {})'.format(self.__pinDefinition.color))
        try:
            self.pwm.stop()
        except Exception as e:
            self.__logger.debug("LedLightPulseProd._pwm_off() - Could not stop pwm, assume not running {}".format(str(e)))

    def cleanup(self):
        self.hardware.cleanup()

    def on(self):
        self.__thread_for_pulse = threading.Thread(target=self._pulse, name="LedPulseThread")
        self.__logger.debug('LedLightPulseProd.on() - Attempt to start pulse in thread')
        try:
            self.__thread_for_pulse.start()
        except Exception as e:
            self.__logger.warning("LedLightPulseProd.on() - Could not start pulsing in thread: {}".format(str(e)))
        self.__logger.debug('LedLightPulseProd.on() - Pulse started in thread')

    def off(self):
        self.__logger.debug("LedLightPulseProd.off()")
        self.__thread_for_pulse.do_run = False
        self.__thread_for_pulse.join()
        self.__logger.debug("LedLightPulseProd.off() - Pulse {} stopped".format(self.__pinDefinition.color))
