#!/usr/bin/env python3

# Called from .bashrc file

import RPi.GPIO as GPIO  # Import the Raspberry Pi GPIO Library

import os
import time
import sys
import pygame
from pygame.locals import *

pygame.init()

# Load the Audio Files
off_hook_audio = pygame.mixer.Sound("/home/davidrobinson/rotary_phone/dialtone.wav")
ring_ring_audio = pygame.mixer.Sound("/home/davidrobinson/rotary_phone/ringringbetter.wav")

# GLobal State Variables
phone_off_hook = False


#Raspberry Pi PINs used
# RuntimeError: Failed to add edge detection when using GPIO 26 on Raspberry Pi 4
off_hook = 37 # GPIO 26 PIN 37
#off_hook = 35 # GPIO 19 PIN 35

# Setup GPIO Board settings
GPIO.setwarnings(False)
# Set the Mode to use the PIN numberings (NOT GPIO numberings)
GPIO.setmode(GPIO.BOARD) # https://raspberrypi.stackexchange.com/questions/12966/what-is-the-difference-between-board-and-bcm-for-gpio-pin-numbering


# Setup GPIO PINs
GPIO.setup(off_hook, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Set PIN 37 to input and pull up to 3.3V

#def off_hook_callback(channel):
#    if GPIO.input(off_hook) == 0:
#       print(channel, "Event Phone is off the hook")
#        off_hook_audio.play()
#        phone_off_hook = True
#    else:
#        print(channel, "Event Phone is on the hook")
#        off_hook_audio.stop()
#        phone_off_hook = False

# Listen for the phone to be picked up
#GPIO.add_event_detect(off_hook, GPIO.BOTH, off_hook_callback, bouncetime=300)

def start_phone_workflow():
    # Play the Dialtone sounds
    off_hook_audio.play()
    # Wait for the user to dial a number
    time.sleep(2)
    # Play the Ring Ring if phone is still off the hook
    if phone_off_hook:
        ring_ring_audio.play()
    # Once this is done, then we play the dialed number audio
    # Monitor for Audio to finish
    while pygame.mixer.get_busy():
        time.sleep(1)
    # Once the audio is done, we hang up the phone
    

print("Monitoring phone status...")
while True:
    time.sleep(0.5)
    # As the off_hook_callback function isn't reliable due to the contacts on the phone being old, we need to check the status of the phone
    if GPIO.input(off_hook) == 0:
        print("Phone is off the hook")
        phone_off_hook = True
        start_phone_workflow()
    else:
        print("Phone is on the hook")
        off_hook_audio.stop()
        ring_ring_audio.stop()
        phone_off_hook = False



# Clean up the GPIO settings when the script is stopped
GPIO.cleanup()
pygame.quit()
