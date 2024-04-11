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
off_hook = 26 # 
dial_pulse = 16 # 

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
cb_counter_handler = pi.callback(dial_pulse, pigpio.RISING_EDGE, dial_monitor) # Set the callback for the dial_pulse PIN.
# The off hook callback is unreliable due to the old contacts on the phone. Only checking pick up the pho. Volts to 0.
cb_off_hook_handler = pi.callback(off_hook, pigpio.FALLING_EDGE, off_hook_callback) # Set the callback for the off_hook PIN.

def start_phone_workflow():
    # Play the Dialtone sounds
    off_hook_audio.play()
    # Wait for the user to dial a number
    while pulse_count < 1:
        # We play the dialtone until a number is dialed or handset put back
        if pi.read(off_hook) == PI_HIGH:
            print("Handset has been put down")
            phone_off_hook = False
            pulse_count = 0
            off_hook_audio.stop()
            return
        time.sleep(0.3)
    off_hook_audio.stop() #  We need to wait for the number to be completed.
    # wait another two second for the dailer to finish before checking the number
    time.sleep(2)
    # count the pulses to find the number
    print("Number of pulses: ", pulse_count)

    if phone_off_hook == True:
        ring_ring_audio.play()
    # Once this is done, then we play the dialed number audio
    # Monitor for Audio to finish
    while pygame.mixer.get_busy():
        # Check is handset has been put down
        if pi.read(off_hook) == PI_HIGH:
            print("Handset has been put down")
            phone_off_hook = False
            pulse_count = 0
            ring_ring_audio.stop()
            off_hook_audio.stop()
            return
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
