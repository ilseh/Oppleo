import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)	# BCM / GIO mode

evse_status_pin=6	# GPIO06 or BOARD PIN 31

# GPIO06 connected to SmartEVSE 12 LED GND pin
# INPUT
# SmartEVSE pulls down (to GND) so pull-up needed GPIO.PUD_UP/GPIO.PUD_DOWN
GPIO.setup(evse_status_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

global revcount
global sliding_window
global min_cnt
revcount = 0
min_cnt = 0
sliding_window = [0] * 60  # sliding window, each entry is a second

def increaserev(channel):
    global revcount
    revcount += 1

# Can add event to GPIO.RISING, GPIO.FALLING, or GPIO.BOTH. For a switch use bouncetime=200
GPIO.add_event_detect(evse_status_pin, GPIO.RISING, callback=increaserev, bouncetime=5)

while True:
    sleep(1)
    sliding_window[min_cnt] = revcount
    min_cnt = (min_cnt +1) % 60
    revcount = 0
    print("RPM is {0}".format(sum(sliding_window)))
    print(" PIN is {0}".format(GPIO.input(evse_status_pin)))
    print(" min_cnt is {0}".format(min_cnt))

