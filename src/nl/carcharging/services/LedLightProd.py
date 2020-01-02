import logging
import threading
import time

try:
    import RPi.GPIO as GPIO
except RuntimeError:
    logging.debug('Assuming dev env')

# TODO: move logic for determining env to reusable position
PROD = 'production'

LED_RED = 13
LED_GREEN = 12
LED_BLUE = 16

PULSE_LED_MIN = 3
PULSE_LED_MAX = 98

# Interval in ms to update led light
FREQ_MS_TO_UPDATE_LED = 10


class LedLightProd(object):
    GPIO.setmode(GPIO.BCM)
    pwm = {}

    def __init__(self, color):
        self.thread_for_pulse = threading.Thread(target=self._pulse)
        self.color = color
        self.logger = logging.getLogger('nl.carcharging.services.LedLighter')

    # TODO: move to a more generic utility class?
    def millis(self):
        return int(round(time.time() * 1000))

    def _init_gpio_pwm(self):
        GPIO.setup(self.color, GPIO.OUT)
        return GPIO.PWM(self.color, 100)

    def _pulse(self):
        pulse_led_value = 0
        pulse_led_millis = 0
        pulse_led_up = True
        self.pwm = self._init_gpio_pwm()
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

        except Exception as ex:
            self.logger.error('Exception pulsing %s' % ex)

        finally:
            self.off()

    def on(self, brightness):
        self.pwm = self._init_gpio_pwm()

        try:
            self.pwm.start(0)
            self.logger.debug('Starting led light %d brightness %d' % (self.color, brightness))
            self.pwm.ChangeDutyCycle(brightness)
        except Exception as ex:
            self.logger.error('Exception lighting led %s' % ex)

    def off(self):
        self.logger.debug('Stopping led light')
        self.pwm.stop()

    def cleanup(self):
        GPIO.cleanup()

    def pulse(self):
        self.thread_for_pulse.start()
        self.logger.debug('Pulse started in thread')

    def pulse_stop(self):
        self.thread_for_pulse.do_run = False
        self.thread_for_pulse.join()
        self.logger.debug('Pulse stopped')
