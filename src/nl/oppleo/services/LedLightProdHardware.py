import logging
import threading

from nl.oppleo.utils.GenericUtil import GenericUtil

GPIO = GenericUtil.importGpio()


class LedLightProdHardware(object):

    def __init__(self, color):
        self.logger = logging.getLogger('nl.oppleo.services.LedLightProdHardware')
        # TODO: check if this lock mechanism is still necessary.
        self.threadLock = threading.Lock()
        self.color = color

    def color_desc(self):
        return {13: 'red', 12: 'green', 16: 'blue'}.get(self.color)

    def init_gpio_pwm(self):

        with self.threadLock:

            pwm = None
            if GPIO is None:
                self.logger.warn("Oppleo LED is enabled but GPIO is not loaded (config error).")
                return None

            for i in range(2):
                try:
                    GPIO.setup(self.color, GPIO.OUT)
                    pwm = GPIO.PWM(self.color, 100)
                except Exception as e:
                    self.logger.warning("Could not initialize GPIO %s, retrying" % e)
                    try:
                        GPIO.cleanup()
                    except Exception as e2:
                        pass # tried to clean
                if pwm:
                    self.logger.debug('pwm initialized')
                    break

            return pwm


    def cleanup(self):

        with self.threadLock:
            # Cleanup resets all ports, also for other still running processes, so don't do that here!
            # GPIO.cleanup()
            pass
