import logging
import threading

from nl.oppleo.utils.GenericUtil import GenericUtil

GPIO = GenericUtil.importGpio()


class LedLightProdHardware(object):

    def __init__(self, color):
        self.logger = logging.getLogger('nl.oppleo.services.LedLightProdHardware')
        # TODO: check if this lock mechanism is still necessary.
        self.lock = threading.Lock()
        self.color = color

    def color_desc(self):
        return {13: 'red', 12: 'green', 16: 'blue'}.get(self.color)

    def init_gpio_pwm(self):
        self.lock.acquire()

        pwm = None
        for i in range(2):
            try:
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
        # Cleanup resets all ports. Need to keep the evse controlled. Let each part cleanop for itseld
        # GPIO.cleanup()
        # self.logger.debug("GPIO cleanup done for %s" % self.color_desc())
        self.lock.release()

