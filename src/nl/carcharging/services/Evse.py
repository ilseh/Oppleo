import logging
import threading

from nl.carcharging.utils.GenericUtil import GenericUtil
from nl.carcharging.config.WebAppConfig import WebAppConfig
from nl.carcharging.utils.WebSocketUtil import WebSocketUtil

GPIO = GenericUtil.importGpio()

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]



class EvseProd(object):
    logger = logging.getLogger('nl.carcharging.services.EvseProd')
    threadLock = None
    try:
        # GPIO.setmode(GPIO.BCM) # Use physical pin numbering
        GPIO.setup(WebAppConfig.pinEvseSwitch, GPIO.OUT, initial=GPIO.HIGH)
    except Exception as ex:
        logger.debug("Could not setmode GPIO, assuming dev env")

    def __init__(self):
        self.threadLock = threading.Lock()


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

"""
  This is a Singleton. This allows the Off Peak status to be stored, and captures EVSE being switched
  ON in off-peak hours before it actually is switched on.
"""
class Evse(object, metaclass=Singleton):
    logger = None
    evse = None
    isOffPeak = False

    def __init__(self):
        self.logger = logging.getLogger('nl.carcharging.services.Evse')
        if GenericUtil.isProd():
            self.logger.debug("Using production Evse")
            self.evse = EvseProd()
        else:
            self.logger.debug("Using fake Evse")
            self.evse = EvseDev()

    def switch_on(self):
        if not WebAppConfig.peakHoursOffPeakEnabled or \
                    self.isOffPeak or \
                    WebAppConfig.peakHoursAllowPeakOnePeriod:
            self.logger.debug('EVSE switched ON (OffPeakEnabled:{}, offPeak={}, PeakAllowed={}).'.format( \
                            WebAppConfig.peakHoursOffPeakEnabled, \
                            self.isOffPeak, \
                            WebAppConfig.peakHoursAllowPeakOnePeriod
                            )
                        )
            self.evse.switch_on()
            WebSocketUtil.emit(
                    event='evse_enabled', 
                    id=WebAppConfig.ENERGY_DEVICE_ID,
                    namespace='/evse_status'
                )

        else:
            self.logger.debug('Evse NOT switched on. Waiting for Off Peak hours')

    def switch_off(self):
        self.evse.switch_off()
        WebSocketUtil.emit(
                event='evse_disabled', 
                id=WebAppConfig.ENERGY_DEVICE_ID,
                namespace='/evse_status'
            )

    def is_enabled(self):
        return self.evse.is_enabled()
