from typing import Optional
import threading
import time
import logging

from nl.oppleo.config.OppleoSystemConfig import OppleoSystemConfig
from nl.oppleo.config.OppleoConfig import OppleoConfig
from nl.oppleo.services.led.RGBLedEffect import RGBLedEffect
from nl.oppleo.services.led.LedPinBehaviour import LedPinBehaviour
from nl.oppleo.utils.ModulePresence import modulePresence

oppleoSystemConfig = OppleoSystemConfig()
oppleoConfig = OppleoConfig()


"""
    RGBLedEffect has the effect per pin
        Available:  red     - off
                    green   - on    100%
                    blue    - off
        Ready:      red     - on    100%
                    green   - on     40%
                    blue    - off
        Charging:   red     - off
                    green   - off
                    blue    - pulse
        Error:      red     - on    100%
                    green   - off
                    blue    - off

    # Obtain the real GPIO object or the stub if GPIO is not installed
    GPIO = modulePresence.GPIO
    # Set the pin-out mode (BOARD or BCM)
    GPIO.setmode(GPIO.BOARD)

    # Setup a pin
    GPIO.setup(self.__pinDefinition.pin, GPIO.OUT)
    # Setup a pin with initial value
    GPIO.setup(channel, GPIO.OUT, initial=GPIO.HIGH)
    # Pull up / Pull down resistors
    GPIO.setup(channel, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    # To read the value of a GPIO pin:
    GPIO.input(channel)

    # To set the output state of a GPIO pin:
    GPIO.output(channel, state)

    # pin and frequency for the pwm
    pwm = GPIO.PWM(self.__pinDefinition.pin, 100)

    To start PWM:
    pwm.start(dc)   # where dc is the duty cycle (0.0 <= dc <= 100.0)

    To change the frequency:
    pwm.ChangeFrequency(freq)   # where freq is the new frequency in Hz

    To change the duty cycle:
    pwm.ChangeDutyCycle(dc)  # where 0.0 <= dc <= 100.0

    To stop PWM:
    pwm.stop()
    Note that PWM will also stop if the instance variable 'p' goes out of scope.

    # Shows the function of a GPIO channel.
    func = GPIO.gpio_function(pin)
    # will return a value from: GPIO.IN, GPIO.OUT, GPIO.SPI, GPIO.I2C, GPIO.HARD_PWM, GPIO.SERIAL, GPIO.UNKNOWN

    # Change the duty cycle
    pwm.ChangeDutyCycle(pulse_led_value)

    If the RGB Led is enabled or disabled, or the pin assignment changes, stop this thread, reset the led effects, and start it again.
"""

class RGBLedControllerThread(object):
    PWM_FREQ = 100                      #
    MAX_SLEEP_TIME = .2                 # Check 5x per second for status updates, including short error pulse
    CHARGE_LED_PULSE_FREQUENCY = 2      # Frequency of led pulses
    ERROR_LED_SWITCH_FREQUENCY = 2      # Frequency of led pulses
    ERROR_FLASH_DURATION_MILLIS = 300   # Duration in millisec of an Error Flash (card rejected etc.)

    logger = None
    threadLock = None
    stopEvent = None

    __openSession = False
    __charging = False
    __error = False
    __errorFlash = False
    __errorFlashStartTime = 0

    __pwmRed = None
    __pwmGreen = None
    __pwmBlue = None


    def resetLedEffects(self):
        global oppleoConfig

        # Solid Green
        self.ledEffectAvailable = RGBLedEffect(
                                    red=LedPinBehaviour(pin=oppleoConfig.pinLedRed),
                                    green=LedPinBehaviour(pin=oppleoConfig.pinLedGreen, 
                                                    low_intensity=100, 
                                                    high_intensity=100
                                                    ),
                                    blue=LedPinBehaviour(pin=oppleoConfig.pinLedBlue),
                                    effect=RGBLedEffect.EFFECT_STATIC,
                                    combinedColorName="Green"
                                    )
        # Solid Yellow
        self.ledEffectReady = RGBLedEffect(
                                red=LedPinBehaviour(pin=oppleoConfig.pinLedRed,
                                                low_intensity=100, 
                                                high_intensity=100
                                                ),
                                green=LedPinBehaviour(pin=oppleoConfig.pinLedGreen, 
                                                low_intensity=40, 
                                                high_intensity=40
                                                ),
                                blue=LedPinBehaviour(pin=oppleoConfig.pinLedBlue),
                                effect=RGBLedEffect.EFFECT_STATIC,
                                combinedColorName="Yellow"
                                )
        # Pulsing Blue
        self.ledEffectCharging = RGBLedEffect(
                                    red=LedPinBehaviour(pin=oppleoConfig.pinLedRed),
                                    green=LedPinBehaviour(pin=oppleoConfig.pinLedGreen),
                                    blue=LedPinBehaviour(pin=oppleoConfig.pinLedBlue, 
                                                    low_intensity=oppleoConfig.pulseLedMin, 
                                                    high_intensity=oppleoConfig.pulseLedMax
                                                    ),
                                    effect=RGBLedEffect.EFFECT_PULSING,
                                    frequency=self.CHARGE_LED_PULSE_FREQUENCY,
                                    combinedColorName="Blue"
                                    )
        # Blinking Red
        self.ledEffectError = RGBLedEffect(
                                red=LedPinBehaviour(pin=oppleoConfig.pinLedRed, 
                                                low_intensity=100, 
                                                high_intensity=100
                                                ),
                                green=LedPinBehaviour(pin=oppleoConfig.pinLedGreen),
                                blue=LedPinBehaviour(pin=oppleoConfig.pinLedBlue),
                                effect=RGBLedEffect.EFFECT_SWITCHING,
                                frequency=self.ERROR_LED_SWITCH_FREQUENCY,
                                combinedColorName="Red"
                                )


    def __init__(self):
        global oppleoConfig
        self.logger = logging.getLogger('nl.oppleo.services.RGBLedControllerThread')

        self.resetLedEffects()
        self.threadLock = threading.Lock()
        self.stopEvent = threading.Event()


    def initLedOutputs(self):
        global modulePresence, oppleoSystemConfig

        GPIO = modulePresence.GPIO
        if oppleoSystemConfig.oppleoLedEnabled:
            GPIO.setup(oppleoConfig.pinLedRed, GPIO.OUT, initial=GPIO.LOW)
            self.__pwmRed = GPIO.PWM(oppleoConfig.pinLedRed, self.PWM_FREQ)
            self.__pwmRed.start(0)
            GPIO.setup(oppleoConfig.pinLedGreen, GPIO.OUT, initial=GPIO.LOW)
            self.__pwmGreen = GPIO.PWM(oppleoConfig.pinLedGreen, self.PWM_FREQ)
            self.__pwmGreen.start(0)
            GPIO.setup(oppleoConfig.pinLedBlue, GPIO.OUT, initial=GPIO.LOW)
            self.__pwmBlue = GPIO.PWM(oppleoConfig.pinLedBlue, self.PWM_FREQ)
            self.__pwmBlue.start(0)



    def cleanLedOutputs(self):
        global modulePresence, oppleoConfig

        GPIO = modulePresence.GPIO

        if self.__pwmRed is not None:
            self.__pwmRed.stop()
            self.__pwmRed = None
        GPIO.cleanup(oppleoConfig.pinLedRed)

        if self.__pwmGreen is not None:
            self.__pwmGreen.stop()
            self.__pwmGreen = None
        GPIO.cleanup(oppleoConfig.pinLedGreen)

        if self.__pwmBlue is not None:
            self.__pwmBlue.stop()
            self.__pwmBlue = None
        GPIO.cleanup(oppleoConfig.pinLedBlue)


    def start(self):
        self.stopEvent.clear()
        self.logger.debug('Launching Thread...')

        self.thread = threading.Thread(target=self.run, name='RGBLedControllerThread')
        self.thread.start()


    def stop(self):
        self.logger.debug(".stop()")
        self.stopEvent.set()


    def __requestedLightEffect__(self) -> RGBLedEffect:
        if self.__errorFlash:
            if ((self.__errorFlashStartTime + self.ERROR_FLASH_DURATION_MILLIS) > (time.time() *1000.0)):
                return self.ledEffectError
            # Done flashing
            self.__errorFlash = False
            self.__errorFlashStartTime = 0
            # On with the normal show
        if self.__error:                # Error
            return self.ledEffectError
        elif self.__openSession:
            if self.__charging:         # Charging
                return self.ledEffectCharging
            else:                       # Ready
                return self.ledEffectReady
        else:                           # Available
            return self.ledEffectAvailable


    def __updateDutyCycle__(self, pwmLed, ledPinBehaviour:Optional[LedPinBehaviour], dutyCyclePercentage:int):
        if pwmLed is None:
            return
        dutyCycle = (ledPinBehaviour.low_intensity +
                        (dutyCyclePercentage * 
                            ((ledPinBehaviour.high_intensity - ledPinBehaviour.low_intensity) /100)
                        )
                    )
        # self.logger.debug("Pin:{}  dc:{} ".format(ledPinBehaviour.pin, dutyCycle))
        pwmLed.ChangeDutyCycle(dutyCycle)


    """
        The active effect is used. For all pins PWM is used, also with DutyCycle 0 (off) or 100 (on).
        The timeDelay is the sleep time, derived from the requested frequency.
    """
    def run(self):
        global modulePresence

        self.logger.info("Starting RGBLedControllerThread")

        # Start the leds all in PWM
        self.initLedOutputs()

        # initial light effect
        activeLightEffect:Optional[RGBLedEffect] = None
        GPIO = modulePresence.GPIO
        timeDelay = self.MAX_SLEEP_TIME
        timeDelayDivider = 1    # If timeDelay is too long, the response becomes sluggish. 
        timeDelayDividerCounter = 0
        dutyCyclePercentage = 0
        dutyCyclePercentageIncrement = 1
        goBrighter:bool = True

        while not self.stopEvent.is_set():
            try:
                requestedLightEffect = self.__requestedLightEffect__()
                if requestedLightEffect != activeLightEffect:
                    # Reset
                    activeLightEffect = requestedLightEffect
                    dutyCyclePercentage = 0
                    goBrighter = True
                    if activeLightEffect.static:
                        # check 5x per second for changes
                        timeDelay = self.MAX_SLEEP_TIME
                        timeDelayDivider = 1
                        # Set the colors once: low + 100% of (high-low)
                        self.__updateDutyCycle__(self.__pwmRed, activeLightEffect.red, 100)
                        self.__updateDutyCycle__(self.__pwmGreen, activeLightEffect.green, 100)
                        self.__updateDutyCycle__(self.__pwmBlue, activeLightEffect.blue, 100)
                        dutyCyclePercentageIncrement = 0
                    if activeLightEffect.switching:
                        # Interval is time in ms for pulse, delay is half pulse in ms (1Hz => 500ms timeDelay)
                        timeDelay = activeLightEffect.frequency /2
                        timeDelayDivider = 1
                        dutyCyclePercentageIncrement = 100
                    if activeLightEffect.pulsing:
                        # Interval is time in ms for 1% increase/decrease (1Hz = 200% (100 up and 100 down) => 5ms timeDelay)
                        timeDelay = activeLightEffect.frequency /200
                        timeDelayDivider = 1
                        dutyCyclePercentageIncrement = 1
                    # Prevent response to become sluggish
                    while timeDelay > self.MAX_SLEEP_TIME:
                        timeDelay = timeDelay /2
                        timeDelayDivider = timeDelayDivider *2
                    timeDelayDividerCounter = 0

                self.logger.debug("run() dutyCyclePercentage:{}".format(dutyCyclePercentage))

                # Run effect if due, skip if divider
                if timeDelayDividerCounter == 0:
                    # Run light effect
                    if activeLightEffect.static:
                        pass
                    if activeLightEffect.switching:
                        self.__updateDutyCycle__(self.__pwmRed, activeLightEffect.red, dutyCyclePercentage)
                        self.__updateDutyCycle__(self.__pwmGreen, activeLightEffect.green, dutyCyclePercentage)
                        self.__updateDutyCycle__(self.__pwmBlue, activeLightEffect.blue, dutyCyclePercentage)
                    if activeLightEffect.pulsing:
                        self.__updateDutyCycle__(self.__pwmRed, activeLightEffect.red, dutyCyclePercentage)
                        self.__updateDutyCycle__(self.__pwmGreen, activeLightEffect.green, dutyCyclePercentage)
                        self.__updateDutyCycle__(self.__pwmBlue, activeLightEffect.blue, dutyCyclePercentage)

                    # Prep next step
                    if goBrighter and dutyCyclePercentage >= 100:
                        goBrighter = False
                    if not goBrighter and dutyCyclePercentage <= 0:
                        goBrighter = True
                    dutyCyclePercentage = ((dutyCyclePercentage + dutyCyclePercentageIncrement) 
                                                if goBrighter else 
                                            (dutyCyclePercentage - dutyCyclePercentageIncrement))
                timeDelayDividerCounter = (timeDelayDividerCounter +1) % timeDelayDivider
                # Yield
                time.sleep(timeDelay)

            except Exception as e:
                self.logger.error("run() Exception controlling the RGB Led", exc_info=True)

        self.logger.info("Stopping RGBLedControllerThread")

        # Start the leds all in PWM
        self.cleanLedOutputs()
    

    @property
    def openSession(self):
        return self.__openSession
            
    @openSession.setter
    def openSession(self, value:bool=False):
        with self.threadLock:
            self.__openSession = value


    @property
    def charging(self):
        return self.__charging
            
    @charging.setter
    def charging(self, value:bool=False):
        with self.threadLock:
            self.__charging = value
            

    @property
    def error(self):
        return self.__error
            
    @error.setter
    def error(self, value:bool=False):
        with self.threadLock:
            self.__error = value
            
    @property
    def errorFlash(self):
        return self.__errorFlash
            
    @errorFlash.setter
    def errorFlash(self, value:bool=False):
        with self.threadLock:
            self.__errorFlash = value
            if value:
                self.__errorFlashStartTime = time.time() *1000.0
            else:
                self.__errorFlashStartTime = 0
                
            
            

