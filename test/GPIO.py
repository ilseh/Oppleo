import RPi.GPIO as GPIO

print("GPIO.BCM: {}".format(GPIO.BCM))
print("GPIO.BOARD: {}".format(GPIO.BOARD))

print("GPIO.IN: {}".format(GPIO.IN))
print("GPIO.OUT: {}".format(GPIO.OUT))
print("GPIO.I2C: {}".format(GPIO.I2C))
print("GPIO.SPI: {}".format(GPIO.SPI))
print("GPIO.HARD_PWM: {}".format(GPIO.HARD_PWM))
print("GPIO.SERIAL: {}".format(GPIO.SERIAL))
print("GPIO.UNKNOWN: {}".format(GPIO.UNKNOWN))

print("GPIO.LOW: {}".format(GPIO.LOW))
print("GPIO.HIGH: {}".format(GPIO.HIGH))

print("GPIO.PUD_DOWN: {}".format(GPIO.PUD_DOWN))
print("GPIO.PUD_UP: {}".format(GPIO.PUD_UP))

print("GPIO.RISING: {}".format(GPIO.RISING))
print("GPIO.FALLING: {}".format(GPIO.FALLING))
print("GPIO.BOTH: {}".format(GPIO.BOTH))

print("GPIO.RPI_INFO: {}".format(GPIO.RPI_INFO))
print("GPIO.RPI_REVISION: {}".format(GPIO.RPI_REVISION))
print("GPIO.VERSION: {}".format(GPIO.VERSION))

gpio_functions = { GPIO.IN:'Input',
   	               GPIO.OUT:'Output',
                   GPIO.I2C:'I2C',
                   GPIO.HARD_PWM:'SPI',
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

print("Done!")
