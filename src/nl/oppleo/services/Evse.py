import logging
import threading

from nl.oppleo.utils.GenericUtil import GenericUtil
from nl.oppleo.config.OppleoSystemConfig import OppleoSystemConfig
from nl.oppleo.config.OppleoConfig import OppleoConfig
from nl.oppleo.utils.WebSocketUtil import WebSocketUtil

oppleoSystemConfig = OppleoSystemConfig()
oppleoConfig = OppleoConfig()

GPIO = GenericUtil.importGpio()

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]



class EvseProd(object):
    logger = logging.getLogger('nl.oppleo.services.EvseProd')
    threadLock = None
    try:
        # GPIO.setmode(GPIO.BCM) # Use physical pin numbering
        GPIO.setup(oppleoConfig.pinEvseSwitch, GPIO.OUT, initial=GPIO.HIGH)
    except Exception as ex:
        logger.debug("Could not setmode GPIO, assuming dev env")

    def __init__(self):
        self.threadLock = threading.Lock()


    def switch_on(self):
        global oppleoConfig

        with self.threadLock:
            self.logger.debug("Product evse on")
            # Setting the output to LOW enables the charging. Keep low.
            try:
                GPIO.output(oppleoConfig.pinEvseSwitch, GPIO.LOW)
            except Exception as e:
                self.logger.debug("Could not setmode GPIO, assuming dev env")





    def switch_off(self):
        global oppleoConfig

        with self.threadLock:
            self.logger.debug("Product Evse off")
            try:
                # Setting the output to HIGH disables the charging. Keep high.
                GPIO.output(oppleoConfig.pinEvseSwitch, GPIO.HIGH)
            except Exception as e:
                self.logger.debug("Could not set GPIO, assuming dev env")

    # Read the state
    def is_enabled(self):
        global oppleoConfig, GPIO

        with self.threadLock:
            if GPIO is None:
                # Assume dev env
                self.logger.debug("Evse.is_enabled() - false as GPIO is None (on dev)")
                return False

            # Note: LOW is ON, and HIGH is OFF
            state = GPIO.input(oppleoConfig.pinEvseSwitch)
            self.logger.debug("Product Evse read state {} (return {})".format(state, (not state)))
            return not GPIO.input(oppleoConfig.pinEvseSwitch)


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
            WebSocketUtil.emit(
                    wsEmitQueue=oppleoConfig.wsEmitQueue,
                    event='evse_enabled', 
                    id=oppleoConfig.chargerName,
                    namespace='/evse_status',
                    public=True
                )

        else:
            self.logger.debug('Evse NOT switched on. Waiting for Off Peak hours')

    def switch_off(self):
        global oppleoConfig

        self.evse.switch_off()
        WebSocketUtil.emit(
                wsEmitQueue=oppleoConfig.wsEmitQueue,
                event='evse_disabled', 
                id=oppleoConfig.chargerName,
                namespace='/evse_status',
                public=True
            )

    def is_enabled(self):
        return self.evse.is_enabled()
