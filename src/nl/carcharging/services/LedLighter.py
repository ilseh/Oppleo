import threading
import time
import logging

from nl.carcharging.utils.GenericUtil import GenericUtil

GPIO = GenericUtil.importGpio()

from nl.carcharging.services.LedLight import LedLight

LIGHT_INTENSITY_LOW = 5
LIGHT_INTENSITY_HIGH = 90


class LedLighter(object):
    logger = logging.getLogger('nl.carcharging.services.LedLighter')
    lock = threading.Lock()

    try:
        GPIO.setmode(GPIO.BCM)
    except Exception as ex:
        logger.debug("Could not setmode of GPIO, assuming dev env")

    def __init__(self):

        self.ledlightAvailable = LedLight(LedLight.LED_GREEN, intensity=LIGHT_INTENSITY_LOW)
        self.ledlightReady = LedLight(LedLight.LED_RED, LedLight.LED_GREEN, intensity=LIGHT_INTENSITY_LOW)
        self.ledlightCharging = LedLight(LedLight.LED_BLUE, pulse=True, intensity=LIGHT_INTENSITY_HIGH)
        self.ledlightError = LedLight(LedLight.LED_RED, intensity=LIGHT_INTENSITY_HIGH)

        # self.ledlight_configs = [self.ledlightAvailable, self.ledlightReady, self.ledlightCharging, self.ledlightError]

        self.current_light = None
        self.previous_light = None

    def back_to_previous_light(self):
        self.switch_to_light(self.previous_light)

    def is_charging_light_on(self):
        return self.current_light == self.ledlightCharging

    def charging(self):
        self.switch_to_light(self.ledlightCharging)

    def available(self):
        self.switch_to_light(self.ledlightAvailable)

    def ready(self):
        self.switch_to_light(self.ledlightReady)

    def switch_to_light(self, light):
        self.lock.acquire()
        self.save_state()
        self.current_light = light
        self.current_light.on()
        self.lock.release()

    def save_state(self):
        self.logger.debug("save state, start comparing")
        if self.previous_light != self.current_light:
            self.logger.debug("save state, previous light is different from current")
            self.previous_light = self.current_light


        if self.previous_light:
            self.logger.debug('turning previous light off')
            self.previous_light.off()
            self.logger.debug('previous light is off')

    def turn_current_light_off(self):
        if self.current_light == self.ledlightCharging:
            self.current_light.pulse_stop()
        else:
            self.current_light.off()

    def error(self, duration=None):
        if duration:
            self.temp_switch_on_thread(self.ledlightError, duration)
        else:
            self.switch_to_light(self.ledlightError)

    def temp_switch_on_thread(self, light, duration):
        thread_for_temp_switch_on = threading.Thread(target=self.temp_switch_on, name="Temp_switch_on thread",
                                                     args=(light, duration))
        thread_for_temp_switch_on.start()

    def temp_switch_on(self, light, duration):

        self.lock.acquire()
        self.save_state()
        self.current_light = light
        self.current_light.on()
        time.sleep(duration)
        self.current_light.off()
        self.current_light = self.previous_light
        self.current_light.on()
        self.lock.release()

    def stop(self):
        lights = {self.ledlightAvailable, self.ledlightReady, self.ledlightError}
        for light in lights:
            light.off()
            light.cleanup()