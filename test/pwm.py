import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

led_red = 16
led_green = 12
led_blue = 13

pin = led_red

gpio_functions = { GPIO.IN:'Input',
   	           GPIO.OUT:'Output',
                   GPIO.I2C:'I2C',
                   GPIO.SPI:'SPI',
                   GPIO.HARD_PWM:'HARD_PWM',
                   GPIO.SERIAL:'Serial',
                   GPIO.UNKNOWN:'Unknown'
                 }

print("GPIO.gpio_function values:")
for key in gpio_functions.keys():
	print(" {}: {}".format(key, gpio_functions[key]))

print("Current GPIO pin config:")
#gpio_pins = (2,3,4,7,8,9,10,11,14,15,17,18,22,23,24,25,27)
gpio_pins = range(0,40)
for gpio_pin in gpio_pins:
    print(" GPIO {} is an {}".format(gpio_pin,gpio_functions[GPIO.gpio_function(gpio_pin)]))

# Check if a PWM output returns PWM or OUT (it's OUT)
print("Check if a PWM output returns PWM or OUT")
print(" Setting pin to GPIO.OUT")
GPIO.setup(pin, GPIO.OUT)

gpioPinFunc = GPIO.gpio_function(pin)
print(" [1] gpioPinFunc: {} ({})".format(gpio_functions[gpioPinFunc],gpioPinFunc))

print(" Setting pin to PWM")
pwm = GPIO.PWM(pin, 100) # 100Hz
pwm.start(20)
pwm.ChangeDutyCycle(50)

gpioPinFunc = GPIO.gpio_function(pin)
print(" [2] gpioPinFunc: {} ({})".format(gpio_functions[gpioPinFunc],gpioPinFunc))

pwm.stop()
GPIO.cleanup(pin)

print(" Setting pin to GPIO.OUT")
GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

gpioPinFunc = GPIO.gpio_function(pin)
print(" [3] gpioPinFunc: {} ({})".format(gpio_functions[gpioPinFunc],gpioPinFunc))
GPIO.cleanup(pin)


# Checking if a pin can be set to OUTPUT twice
# - yes, no warning. Only RuntimeWarning if set by other process
print("Checking if a pin can be set to OUTPUT twice")

print(" Setting pin to GPIO.OUT")
GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

print(" Setting pin to GPIO.OUT")
GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

GPIO.cleanup(pin)


# Checking if a second PWM can be created (no)
print("Checking if a second PWM can be created")

print(" Setting pin to GPIO.OUT")
GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

print(" Setting pin to PWM")
pwm = GPIO.PWM(pin, 100) # 100Hz
pwm.start(20)
pwm.ChangeDutyCycle(50)

print(" Obtaining yet another PWM")
try:
	pwm = GPIO.PWM(pin, 100) # 100Hz
except RuntimeError as rte:
	print("  RuntimeError {}".format(rte))
pwm.start(20)
pwm.ChangeDutyCycle(50)

GPIO.cleanup(pin)

print("Current GPIO pin config:")
for gpio_pin in gpio_pins:
    print(" GPIO {} is an {}".format(gpio_pin,gpio_functions[GPIO.gpio_function(gpio_pin)]))


print("Done!")
