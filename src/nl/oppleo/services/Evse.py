import logging
import threading

from nl.oppleo.utils.ModulePresence import ModulePresence
from nl.oppleo.config.OppleoSystemConfig import OppleoSystemConfig
from nl.oppleo.config.OppleoConfig import OppleoConfig
from nl.oppleo.utils.OutboundEvent import OutboundEvent

oppleoSystemConfig = OppleoSystemConfig()
oppleoConfig = OppleoConfig()
modulePresence = ModulePresence()

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class EvseProd(object):
    logger = logging.getLogger('nl.oppleo.services.EvseProd')
    threadLock = None

    def __init__(self):
        global oppleoConfig, modulePresence

        self.threadLock = threading.Lock()
        if not modulePresence.gpioAvailable():
            self.logger.debug("EvseProd.__init__() - GPIO not loaded")
        else:
            GPIO = modulePresence.GPIO
            try:
                # GPIO.setmode(GPIO.BCM) # Use physical pin numbering
                GPIO.setup(oppleoConfig.pinEvseSwitch, GPIO.OUT, initial=GPIO.HIGH)
            except Exception as e:
                self.logger.debug("EvseProd.__init__() - Could not set pin {} to {} with initial {}".format(
                    oppleoConfig.pinEvseSwitch, GPIO.OUT, GPIO.HIGH
                ))


    def switch_on(self):
        global oppleoConfig, modulePresence

        if not modulePresence.gpioAvailable():
            self.logger.debug("EvseProd.switch_on() - GPIO not loaded")
            return

        with self.threadLock:

            GPIO = modulePresence.GPIO
            self.logger.debug("EvseProd.switch_on() - on")
            # Setting the output to LOW enables the charging. Keep low.
            try:
                GPIO.output(oppleoConfig.pinEvseSwitch, GPIO.LOW)
            except Exception as e:
                self.logger.debug("EvseProd.switch_on() - Could not set pin {} output to {}".format(
                    oppleoConfig.pinEvseSwitch, GPIO.LOW
                ))



    def switch_off(self):
        global oppleoConfig, modulePresence

        if not modulePresence.gpioAvailable():
            self.logger.debug("EvseProd.switch_off() - GPIO not loaded")
            return

        with self.threadLock:
            GPIO = modulePresence.GPIO
            self.logger.debug("EvseProd.switch_off() - off")
            try:
                # Setting the output to HIGH disables the charging. Keep high.
                GPIO.output(oppleoConfig.pinEvseSwitch, GPIO.HIGH)
            except Exception as e:
                self.logger.debug("EvseProd.switch_off() - Could not set pin {} output to {}".format(
                    oppleoConfig.pinEvseSwitch, GPIO.HIGH
                ))


    # Read the state
    def is_enabled(self) -> bool:
        global oppleoConfig, modulePresence

        if not modulePresence.gpioAvailable():
            self.logger.debug("EvseProd.is_enabled() - GPIO not loaded")
            return False

        with self.threadLock:
            GPIO = modulePresence.GPIO
            self.logger.debug("EvseProd.is_enabled()")

            # Note: LOW is ON, and HIGH is OFF
            state = GPIO.input(oppleoConfig.pinEvseSwitch)
            self.logger.debug("EvseProd.is_enabled() - Evse read state {} (return {})".format(state, (not state)))
            return not state


class EvseDev(object):
    logger = logging.getLogger('nl.oppleo.services.EvseDev')

    def switch_on(self):
        self.logger.debug("Fake turn evse on")

    def switch_off(self):
        self.logger.debug("Fake turn evse off")

    def is_enabled(self):
        self.logger.debug("Fake read evse state")
        return False

"""
  This is a Singleton. This allows the Off Peak status to be stored, and captures EVSE being switched
  ON in off-peak hours before it actually is switched on.
"""
class Evse(object, metaclass=Singleton):
    logger = None
    evse = None
    isOffPeak = False

    def __init__(self):
        self.logger = logging.getLogger('nl.oppleo.services.Evse')
        if oppleoSystemConfig.evseSwitchEnabled:
            self.logger.debug("Using production Evse")
            self.evse = EvseProd()
        else:
            self.logger.debug("Using fake Evse")
            self.evse = EvseDev()

    def switch_on(self):
        global oppleoConfig

        if not oppleoConfig.offpeakEnabled or \
                    self.isOffPeak or \
                    oppleoConfig.allowPeakOnePeriod:
            self.logger.debug('EVSE switched ON (OffPeakEnabled:{}, offPeak={}, PeakAllowed={}).'.format( \
                            oppleoConfig.offpeakEnabled, \
                            self.isOffPeak, \
                            oppleoConfig.allowPeakOnePeriod
                            )
                        )
            self.evse.switch_on()
            OutboundEvent.triggerEvent(
                event='evse_enabled', 
                id=oppleoConfig.chargerID,
                namespace='/evse_status',
                public=True
            )

        else:
            self.logger.debug('Evse NOT switched on. Waiting for Off Peak hours')

    def switch_off(self):
        global oppleoConfig

        self.evse.switch_off()
        OutboundEvent.triggerEvent(
            event='evse_disabled', 
            id=oppleoConfig.chargerID,
            namespace='/evse_status',
            public=True
        )

    def is_enabled(self):
        return self.evse.is_enabled()
