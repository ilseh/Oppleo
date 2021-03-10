import threading
import time
import logging

from nl.oppleo.config.OppleoConfig import OppleoConfig
from nl.oppleo.services.LedPinDefinition import LedPinDefinition
from nl.oppleo.utils.GenericUtil import GenericUtil

oppleoConfig = OppleoConfig()
GPIO = GenericUtil.importGpio()

from nl.oppleo.services.LedLight import LedLight

LIGHT_INTENSITY_LOW = 5
LIGHT_INTENSITY_HIGH = 90


class LedLighter(object):
    logger = logging.getLogger('nl.oppleo.services.LedLighter')
    lock = threading.Lock()

    def __init__(self):
        global oppleoConfig

#        self.ledlightAvailable = LedLight(oppleoConfig.pinLedGreen, intensity=LIGHT_INTENSITY_LOW)
        self.ledlightAvailable = LedLight(
                                    LedPinDefinition(pin=oppleoConfig.pinLedGreen, color="Green"),
                                    combinedColorName="Green",
                                    intensity=LIGHT_INTENSITY_LOW
                                    )
#        self.ledlightReady = LedLight(oppleoConfig.pinLedRed, oppleoConfig.pinLedGreen, intensity=LIGHT_INTENSITY_LOW)
        self.ledlightReady = LedLight(
                                LedPinDefinition(pin=oppleoConfig.pinLedRed, color="Red"),
                                LedPinDefinition(pin=oppleoConfig.pinLedGreen, color="Green"),
                                combinedColorName="Yellow",
                                intensity=LIGHT_INTENSITY_LOW
                                )
#        self.ledlightCharging = LedLight(oppleoConfig.pinLedBlue, pulse=True, intensity=LIGHT_INTENSITY_HIGH)
        self.ledlightCharging = LedLight(
                                    LedPinDefinition(pin=oppleoConfig.pinLedBlue, color="Blue"),
                                    combinedColorName="Blue",
                                    pulse=True, 
                                    intensity=LIGHT_INTENSITY_HIGH
                                    )
#        self.ledlightError = LedLight(oppleoConfig.pinLedRed, intensity=LIGHT_INTENSITY_HIGH)
        self.ledlightError = LedLight(
                                LedPinDefinition(pin=oppleoConfig.pinLedRed, color="Red"),
                                combinedColorName="Red",
                                intensity=LIGHT_INTENSITY_HIGH
                                )

        # self.ledlight_configs = [self.ledlightAvailable, self.ledlightReady, self.ledlightCharging, self.ledlightError]

        self.current_light = None
        self.previous_light = None

    def back_to_previous_light(self):
        self.logger.debug("LedLighter.back_to_previous_light()")
        self.switch_to_light(self.previous_light)

    def is_charging_light_on(self):
        # self.logger.debug("LedLighter.is_charging_light_on()")
        return self.current_light == self.ledlightCharging

    def charging(self):
        self.logger.debug("LedLighter.charging()")
        self.switch_to_light(self.ledlightCharging)

    def available(self):
        self.logger.debug("LedLighter.available()")
        self.switch_to_light(self.ledlightAvailable)

    def ready(self):
        self.logger.debug("LedLighter.ready()")
        self.switch_to_light(self.ledlightReady)

    def switch_to_light(self, light):
        self.logger.debug("LedLighter.switch_to_light()")
        with self.lock:
            self.save_state()
            self.current_light = light
            self.current_light.on()


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
        self.logger.debug("LedLighter.turn_current_light_off()")
        if self.current_light == self.ledlightCharging:
            self.current_light.pulse_stop()
        else:
            self.current_light.off()

    def error(self, duration=None):
        self.logger.debug("LedLighter.error()")
        if duration:
            self.temp_switch_on_thread(self.ledlightError, duration)
        else:
            self.switch_to_light(self.ledlightError)

    def temp_switch_on_thread(self, light, duration):
        self.logger.debug("LedLighter.temp_switch_on_thread()")
        thread_for_temp_switch_on = threading.Thread(target=self.temp_switch_on, 
                                                     name="TempSwitchOnThread",
                                                     args=(light, duration)
                                                     )
        thread_for_temp_switch_on.start()


    def temp_switch_on(self, light, duration):
        self.logger.debug("LedLighter.temp_switch_on()")
        with self.lock:
            self.save_state()
            self.current_light = light
            self.current_light.on()
            time.sleep(duration)
            self.current_light.off()
            self.current_light = self.previous_light
            self.current_light.on()


    def stop(self):
        self.logger.debug("LedLighter.stop()")
        lights = {self.ledlightAvailable, self.ledlightReady, self.ledlightError}
        for light in lights:
            light.off()
            light.cleanup()