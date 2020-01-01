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
    pulseLedValue = 0
    pulseLedMillis = 0
    pulseLedUp = True


    def __init__(self, color):
        self.t = threading.Thread(target=self._pulse)
        self.color = color
        self.logger = logging.getLogger('nl.carcharging.services.LedLighter')

    # TODO: move to a more generic utility class?
    def millis(self):
        return int(round(time.time() * 1000))

    def _pulse(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.color, GPIO.OUT)
        pwm = GPIO.PWM(self.color, 100)

        try:
            pwm.start(0)
            self.logger.debug('Starting led pulse')
            t = threading.currentThread()
            while getattr(t, "do_run", True):
                if self.millis() > (self.pulseLedMillis + FREQ_MS_TO_UPDATE_LED):
                    if ((self.pulseLedUp and (self.pulseLedValue >= PULSE_LED_MAX)) or
                            ((not self.pulseLedUp) and (self.pulseLedValue <= PULSE_LED_MIN))):
                        self.pulseLedUp = not self.pulseLedUp
                    if self.pulseLedUp:
                        self.pulseLedValue += 1
                    else:
                        self.pulseLedValue -= 1
                    pwm.ChangeDutyCycle(self.pulseLedValue)
                    self.logger.debug("pulseLedValue = ", self.pulseLedValue)
                    self.pulseLedMillis = self.millis()

        except Exception as ex:
            self.logger.error('Exception pulsing development %s' % ex)

        finally:
            self.logger.debug('Stopping led pulse')
            pwm.stop()
            GPIO.cleanup()


    def pulse(self):
        self.t.start()
        self.logger.debug('Pulse started in thread')


    def stop(self):
        self.t.do_run = False
        self.t.join()
        self.logger.debug('Pulse stopped')


