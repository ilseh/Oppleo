import logging
import threading

try:
    import RPi.GPIO as GPIO
except RuntimeError:
    logging.debug('Assuming dev env')


class LedLightProdHardware(object):

    def __init__(self):
        # TODO: check if this lock mechanism is still necessary.
        self.lock = threading.Lock()

    @staticmethod
    def color_desc(color):
        return {13: 'red', 12: 'green', 16: 'blue'}.get(color)

    def init_gpio_pwm(self):
        self.lock.acquire()

        for i in range(2):
            try:
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(self.color, GPIO.OUT)
                pwm = GPIO.PWM(self.color, 100)
            except Exception as ex:
                self.logger.warning("Could not initialize GPIO %s, retrying" % ex)
                GPIO.cleanup()
            if pwm:
                self.logger.debug('pwm initialized')
                break

        self.lock.release()
        return pwm


    def cleanup(self):
        self.lock.acquire()
        GPIO.cleanup()
        self.logger.debug("GPIO cleanup done for %s" % self.color_desc())
        self.lock.release()

