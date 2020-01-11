import time
import logging

try:
    import RPi.GPIO as GPIO
except RuntimeError:
    logging.debug('Assuming dev env')

from nl.carcharging.services.LedLight import LedLight

LIGHT_INTENSITY_LOW = 5
LIGHT_INTENSITY_HIGH = 90


class LedLighter(object):
    GPIO.setmode(GPIO.BCM)

    def __init__(self):

        self.ledlightAvailable = LedLight(LedLight.LED_GREEN)
        self.ledlightReady = LedLight(LedLight.LED_RED, LedLight.LED_GREEN)
        self.ledlightCharging = LedLight(LedLight.LED_BLUE, pulse=True)
        self.ledlightError = LedLight(LedLight.LED_RED)

        # self.ledlight_configs = [self.ledlightAvailable, self.ledlightReady, self.ledlightCharging, self.ledlightError]

        self.current_light = None
        self.previous_light = None

    def back_to_previous_light(self):
        self.switch_to_light(self.previous_light)

    def is_charging_light_on(self):
        return self.current_light == self.ledlightCharging

    def charging(self):
        self.switch_to_light(self.ledlightCharging, LIGHT_INTENSITY_LOW)

    def available(self):
        self.switch_to_light(self.ledlightAvailable, LIGHT_INTENSITY_LOW)

    def ready(self):
        self.switch_to_light(self.ledlightReady, LIGHT_INTENSITY_LOW)

    def switch_to_light(self, light, intensity):
        self.save_state()
        self.current_light = light
        self.current_light.on(intensity)

    def save_state(self):
        self.previous_light = self.current_light
        if self.previous_light:
            self.previous_light.off()

    def turn_current_light_off(self):
        if self.current_light == self.ledlightCharging:
            self.current_light.pulse_stop()
        else:
            self.current_light.off()

    def error(self, duration=None):
        if duration:
            self.temp_switch_on(self.ledlightError, LIGHT_INTENSITY_HIGH, duration)
        else:
            self.switch_to_light(self.ledlightError, LIGHT_INTENSITY_HIGH)

    def temp_switch_on(self, light, brightness, duration):
        self.previous_light = self.current_light
        self.current_light.off()
        self.current_light = light
        self.current_light.on(brightness)
        time.sleep(duration)
        self.current_light.off()
        self.current_light = self.previous_light
        self.current_light.on(self.current_light.brightness)

    def stop(self):
        lights = {self.ledlightAvailable, self.ledlightReady, self.ledlightError}
        for light in lights:
            light.off()
            light.cleanup()