import logging
import threading

from nl.carcharging.utils.GenericUtil import GenericUtil
from nl.carcharging.config.WebAppConfig import WebAppConfig
from threading import Lock

GPIO = GenericUtil.importGpio()


class EvseProd(object):
    logger = logging.getLogger('nl.carcharging.services.EvseProd')
    threadLock = None
    try:
        # GPIO.setmode(GPIO.BCM) # Use physical pin numbering
        GPIO.setup(WebAppConfig.pinEvseSwitch, GPIO.OUT, initial=GPIO.HIGH)
    except Exception as ex:
        logger.debug("Could not setmode GPIO, assuming dev env")

    def __init__(self):
        self.threadLock = Lock()


    def switch_on(self):
        global WebAppConfig

        with self.threadLock:
            self.logger.debug("Product evse on")
            # Setting the output to LOW enables the charging. Keep low.
            GPIO.output(WebAppConfig.pinEvseSwitch, GPIO.LOW)


    def switch_off(self):
        global WebAppConfig

        with self.threadLock:
            self.logger.debug("Product Evse off")
            # Setting the output to HIGH disables the charging. Keep high.
            GPIO.output(WebAppConfig.pinEvseSwitch, GPIO.HIGH)

    # Read the state
    def is_enabled(self):
        global WebAppConfig

        with self.threadLock:
            # Note: LOW is ON, and HIGH is OFF
            state = GPIO.input(WebAppConfig.pinEvseSwitch)
            self.logger.debug("Product Evse read state {} (return {})".format(state, (not state)))
            return not GPIO.input(WebAppConfig.pinEvseSwitch)


class EvseDev(object):
    logger = logging.getLogger('nl.carcharging.services.EvseDev')

    def switch_on(self):
        self.logger.debug("Fake turn evse on")

    def switch_off(self):
        self.logger.debug("Fake turn evse off")

    def is_enabled(self):
        self.logger.debug("Fake read evse state")
        return True


class Evse(object):

    def __init__(self):
        self.logger = logging.getLogger('nl.carcharging.services.Evse')
        if GenericUtil.isProd():
            self.logger.debug("Using production Evse")
            self.evse = EvseProd();
        else:
            self.logger.debug("Using fake Evse")
            self.evse = EvseDev()

    def switch_on(self):
        self.evse.switch_on()

    def switch_off(self):
        self.evse.switch_off()

    def is_enabled(self):
        return self.evse.is_enabled()
