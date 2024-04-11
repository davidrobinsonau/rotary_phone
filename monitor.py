#!/usr/bin/env python3

# Called from .bashrc file

import RPi.GPIO as GPIO  # Import the Raspberry Pi GPIO Library

import os
import time
import sys
import pygame
from pygame.locals import *
# Import the pigpio library for the rotary pulses. The standard GPIO Python library isn't fast enough to detect the pulses
import pigpio

PI_HIGH = 1
PI_LOW = 0

# Initialize the Pygame library
pygame.init()

# PiGPIO library instance, globally defined
pi = pigpio.pi()

# Load the Audio Files
off_hook_audio = pygame.mixer.Sound("/home/davidrobinson/rotary_phone/dialtone.wav")
ring_ring_audio = pygame.mixer.Sound("/home/davidrobinson/rotary_phone/ringringbetter.wav")
# Array of the audio files for the numbers. Will copy from the repository to the boot directory
audio_files = [
    pygame.mixer.Sound("/boot/0.wav"),
    pygame.mixer.Sound("/boot/1.wav"),
    pygame.mixer.Sound("/boot/2.wav"),
    pygame.mixer.Sound("/boot/3.wav"),
    pygame.mixer.Sound("/boot/4.wav"),
    pygame.mixer.Sound("/boot/5.wav"),
    pygame.mixer.Sound("/boot/6.wav"),
    pygame.mixer.Sound("/boot/7.wav"),
    pygame.mixer.Sound("/boot/8.wav"),
    pygame.mixer.Sound("/boot/9.wav"),
]

# GLobal State Variables
phone_off_hook = False

# Count the pulses
pulse_count = 0

#Raspberry Pi PINs used
# RuntimeError: Failed to add edge detection when using GPIO 26 on Raspberry Pi 4
off_hook = 37 # GPIO 26 PIN 37
#off_hook = 35 # GPIO 19 PIN 35
dial_pulse = 16 # GPIO 16 PIN 36 PIGIO uses the GPIO numbering

# Setup GPIO Board settings
GPIO.setwarnings(False)
# Set the Mode to use the PIN numberings (NOT GPIO numberings)
GPIO.setmode(GPIO.BOARD) # https://raspberrypi.stackexchange.com/questions/12966/what-is-the-difference-between-board-and-bcm-for-gpio-pin-numbering


# Setup GPIO PINs
GPIO.setup(off_hook, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Set PIN 37 to input and pull up to 3.3V
GPIO.setup(dial_pulse, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Set PIN 36 to input and pull up to 3.3V

def off_hook_callback(channel):
    if GPIO.input(off_hook) == 1:
        print(channel, "Event Phone is on the hook. Stopping Audio.")
        phone_off_hook = False
        ring_ring_audio.stop()
        off_hook_audio.stop()
  
def dial_monitor(channel):
    pulse_count += 1
    print(channel, pulse_count, " Dial Event Detected")


# Listen for the phone to be picked up
GPIO.add_event_detect(off_hook, GPIO.FALLING, off_hook_callback, bouncetime=300)
#GPIO.add_event_detect(dial_pulse, GPIO.FALLING, dial_monitor, bouncetime=300) # This is disabled as the pulse is too fast for the GPIO library to detect
pi.set_mode(dial_pulse, pigpio.INPUT)
pi.set_pull_up_down(dial_pulse, pigpio.PUD_UP) # Set the pull up resistor on the dial_pulse PIN
cb_counter_handler = pi.callback(dial_pulse, pigpio.EITHER_EDGE, dial_monitor) # Set the callback for the dial_pulse PIN

def start_phone_workflow():
    # Play the Dialtone sounds
    if GPIO.input(off_hook) == 0: # Check if the phone is still off the hook
        off_hook_audio.play()
    # Wait for the user to dial a number
    time.sleep(2)
    off_hook_audio.stop() # For testing
    # Play the Ring Ring if phone is still off the hook
    if GPIO.input(off_hook) == 0:
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
