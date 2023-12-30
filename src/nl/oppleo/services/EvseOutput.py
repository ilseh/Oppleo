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


class EvseOutputGenerator(object):
    logger = logging.getLogger('nl.oppleo.services.EvseOutputGenerator')
    threadLock = None

    def __init__(self):
        global oppleoConfig, modulePresence

        self.threadLock = threading.Lock()
        if not modulePresence.gpioAvailable():
            self.logger.debug("EvseOutputGenerator.__init__() - GPIO not loaded")
        else:
            GPIO = modulePresence.GPIO
            try:
                # GPIO.setmode(GPIO.BCM) # Use physical pin numbering
                GPIO.setup(oppleoConfig.pinEvseSwitch, GPIO.OUT, initial=GPIO.HIGH)
            except Exception as e:
                self.logger.debug("EvseOutputGenerator.__init__() - Could not set pin {} to {} with initial {}".format(
                    oppleoConfig.pinEvseSwitch, GPIO.OUT, GPIO.HIGH
                ))


    def switch_on(self):
        global oppleoConfig, modulePresence

        if not modulePresence.gpioAvailable():
            self.logger.debug("EvseOutputGenerator.switch_on() - GPIO not loaded")
            return

        with self.threadLock:

            GPIO = modulePresence.GPIO
            self.logger.debug("EvseOutputGenerator.switch_on() - on")
            # Setting the output to LOW enables the charging. Keep low.
            try:
                GPIO.output(oppleoConfig.pinEvseSwitch, GPIO.LOW)
            except Exception as e:
                self.logger.debug("EvseOutputGenerator.switch_on() - Could not set pin {} output to {}".format(
                    oppleoConfig.pinEvseSwitch, GPIO.LOW
                ))



    def switch_off(self):
        global oppleoConfig, modulePresence

        if not modulePresence.gpioAvailable():
            self.logger.debug("EvseOutputGenerator.switch_off() - GPIO not loaded")
            return

        with self.threadLock:
            GPIO = modulePresence.GPIO
            self.logger.debug("EvseOutputGenerator.switch_off() - off")
            try:
                # Setting the output to HIGH disables the charging. Keep high.
                GPIO.output(oppleoConfig.pinEvseSwitch, GPIO.HIGH)
            except Exception as e:
                self.logger.debug("EvseOutputGenerator.switch_off() - Could not set pin {} output to {}".format(
                    oppleoConfig.pinEvseSwitch, GPIO.HIGH
                ))


    # Read the state
    def is_enabled(self) -> bool:
        global oppleoConfig, modulePresence

        if not modulePresence.gpioAvailable():
            self.logger.debug("EvseOutputGenerator.is_enabled() - GPIO not loaded")
            return False

        with self.threadLock:
            GPIO = modulePresence.GPIO
            self.logger.debug("EvseOutputGenerator.is_enabled()")

            # Note: LOW is ON, and HIGH is OFF
            state = GPIO.input(oppleoConfig.pinEvseSwitch)
            self.logger.debug("EvseOutputGenerator.is_enabled() - Evse read state {} (return {})".format(state, (not state)))
            return not state


class EvseOutputSimulator(object):
    __logger = logging.getLogger('nl.oppleo.services.EvseOutputSimulator')
    __simulatedEvseOutputState = False

    def switch_on(self):
        self.__logger.debug("Turn EVSE output simulator ON")
        self.__simulatedEvseOutputState = True

    def switch_off(self):
        self.__logger.debug("Turn EVSE output simulator OFF")
        self.__simulatedEvseOutputState = False

    def is_enabled(self):
        self.__logger.debug("Return simulated EVSE output state (state={})".format(self.__simulatedEvseOutputState))
        return self.__simulatedEvseOutputState

"""
  This is a Singleton. This allows the Off Peak status to be stored, and captures EVSE being switched
  ON in off-peak hours before it actually is switched on.
"""
class EvseOutput(object, metaclass=Singleton):
    logger = None
    evseOutput = None
    isOffPeak = False

    def __init__(self):
        self.logger = logging.getLogger('nl.oppleo.services.EvseOutput')
        if oppleoSystemConfig.evseSwitchEnabled:
            self.logger.debug("Using real Evse Output Generator")
            self.evseOutput = EvseOutputGenerator()
        else:
            self.logger.debug("Evse Output not enabled, using Evse Output Simulator")
            self.evseOutput = EvseOutputSimulator()

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
            self.evseOutput.switch_on()
            OutboundEvent.triggerEvent(
                event='evse_enabled', 
                id=oppleoConfig.chargerID,
                namespace='/evse_status',
                public=True
            )

        else:
            self.logger.debug('Evse utput NOT switched on. Waiting for Off Peak hours')

    def switch_off(self):
        global oppleoConfig

        self.evseOutput.switch_off()
        OutboundEvent.triggerEvent(
            event='evse_disabled', 
            id=oppleoConfig.chargerID,
            namespace='/evse_status',
            public=True
        )

    def is_enabled(self):
        return self.evseOutput.is_enabled()
