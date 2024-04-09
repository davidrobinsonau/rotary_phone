#!/usr/bin/env python3

import RPi.GPIO as GPIO  # Import the Raspberry Pi GPIO Library

import os
import time
import sys

#Raspberry Pi PINs used
off_hook = 26 # GPIO 26 PIN 37

# Setup GPIO Board settings
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

# Setup GPIO PINs
GPIO.setup(off_hook, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Set PIN 37 to input and pull up to 3.3V

def off_hook_callback(channel):
    if GPIO.input(off_hook) == 0:
        print(channel, "Phone is off the hook")
    else:
        print(channel, "Phone is on the hook")

# Listen for the phone to be picked up
GPIO.add_event_detect(off_hook, GPIO.BOTH, off_hook_callback, bouncetime=100)


while True:
    time.sleep(1)
