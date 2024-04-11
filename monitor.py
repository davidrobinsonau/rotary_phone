#!/usr/bin/env python3

# Called from .bashrc file

#import RPi.GPIO as GPIO  # Import the Raspberry Pi GPIO Library

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

# Define the GPIO PINs
off_hook = 25 # GPIO 25 PIN 37 PIGIO uses the GPIO numbering
dial_pulse = 27 # GPIO 27 PIN 36 PIGIO uses the GPIO numbering

# Setup GPIO Board settings
# GPIO.setwarnings(False)
# Set the Mode to use the PIN numberings (NOT GPIO numberings)
#GPIO.setmode(GPIO.BOARD) # https://raspberrypi.stackexchange.com/questions/12966/what-is-the-difference-between-board-and-bcm-for-gpio-pin-numbering


# Setup GPIO PINs
#GPIO.setup(off_hook, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Set PIN 37 to input and pull up to 3.3V
#GPIO.setup(dial_pulse, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Set PIN 36 to input and pull up to 3.3V

def off_hook_callback(GPIO_Channel, event, tick):
    global phone_off_hook
    global pulse_count
    # Check if the phone is off the hook or on the hook
    if event == 0:
        #  = change to low (a falling edge) which means the phone is off the hook and in someones hand.
        print(GPIO_Channel, "Phone Handset has been picked up")
        phone_off_hook = True
        # start_phone_workflow()
    if event == 1:
        # 1 = change to high (a rising edge) which means the phone is on the hook ie placed back on the cradle
        print(GPIO_Channel, "Phone Handset has been put down")
        phone_off_hook = False
        ring_ring_audio.stop()
        off_hook_audio.stop()
        # Reset pulse count to zero
        pulse_count = 0
  
def dial_monitor(GPIO_Channel, event, tick):
    '''
    The user supplied callback receives three parameters, the GPIO, the level, and the tick.
    Parameter   Value    Meaning
    GPIO        0-31     The GPIO which has changed state
    level       0-2      0 = change to low (a falling edge)
                         1 = change to high (a rising edge)
                         2 = no level change (a watchdog timeout)
    tick        32 bit   The number of microseconds since boot
                         WARNING: this wraps around from
                         4294967295 to 0 roughly every 72 minutes
    '''
    global pulse_count
    pulse_count += 1
    print(GPIO_Channel,event, tick , pulse_count, " Dial Event Detected")


# Listen for the phone to be picked up
#GPIO.add_event_detect(off_hook, GPIO.FALLING, off_hook_callback, bouncetime=300)
#GPIO.add_event_detect(dial_pulse, GPIO.FALLING, dial_monitor, bouncetime=300) # This is disabled as the pulse is too fast for the GPIO library to detect

pi.set_mode(off_hook, pigpio.INPUT)
pi.set_pull_up_down(off_hook, pigpio.PUD_UP) # Set the pull up resistor on the off_hook PIN

pi.set_mode(dial_pulse, pigpio.INPUT)
pi.set_pull_up_down(dial_pulse, pigpio.PUD_UP) # Set the pull up resistor on the dial_pulse PIN

# 
cb_counter_handler = pi.callback(dial_pulse, pigpio.EITHER_EDGE, dial_monitor) # Set the callback for the dial_pulse PIN
cb_off_hook_handler = pi.callback(off_hook, pigpio.EITHER_EDGE, off_hook_callback) # Set the callback for the off_hook PIN

def start_phone_workflow():
    # Play the Dialtone sounds
    off_hook_audio.play()
    # Wait for the user to dial a number
    time.sleep(2)
    off_hook_audio.stop() # For testing
    # Play the Ring Ring if phone is still off the hook
    if phone_off_hook == True:
        ring_ring_audio.play()
    # Once this is done, then we play the dialed number audio
    # Monitor for Audio to finish
    while pygame.mixer.get_busy():
        time.sleep(0.5)
    # Once the audio is done, we hang up the phone
    

print("Monitoring phone status...")
while True:
    time.sleep(0.5)
    # As the off_hook_callback function isn't reliable due to the contacts on the phone being old, we need to check the status of the phone
    print("State: Off-Hook: ",pi.read(off_hook), " Dial Pulse: ", pi.read(dial_pulse))
    if phone_off_hook:
        start_phone_workflow()



# Clean up the GPIO settings when the script is stopped
GPIO.cleanup()
pygame.quit()
