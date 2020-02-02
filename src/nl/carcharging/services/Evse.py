import logging

from nl.carcharging.utils.GenericUtil import GenericUtil

GPIO = GenericUtil.importGpio()

switch_pin = 5  # GPIO5 pin 29

class EvseProd(object):
    logger = logging.getLogger('nl.carcharging.services.EvseProd')

    try:
        GPIO.setmode(GPIO.BCM) # Use physical pin numbering
        GPIO.setup(switch_pin, GPIO.OUT, initial=GPIO.HIGH)
    except Exception as ex:
        logger.debug("Could not setmode GPIO, assuming dev env")


    def switch_on(self):
        self.logger.debug("Product evse on")
        # Setting the output to LOW enables the charging. Keep low.
        GPIO.output(switch_pin, GPIO.LOW)


    def switch_off(self):
        self.logger.debug("Product Evse off")
        # Setting the output to HIGH disables the charging. Keep high.
        GPIO.output(switch_pin, GPIO.HIGH)


class EvseDev(object):
    logger = logging.getLogger('nl.carcharging.services.EvseDev')

    def switch_on(self):
        self.logger.debug("Fake turn evse on")

    def switch_off(self):
        self.logger.debug("Fake turn evse off")

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
