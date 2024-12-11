#!/usr/bin/env python3
# Called from .bashrc file
# This script is used to monitor the phone status and dial pulses to play the audio files through the DF Player Pro board and speaker.
# https://wiki.dfrobot.com/DFPlayer_PRO_SKU_DFR0768
# The script will play the dialtone when the phone is picked up and then play the audio files for the number dialed.

# This is version 2 of the script, using the DF Player Pro and a Raspberry Pi Zero 2 W to monitor the dialing mechanism.

# Switch to detach that the handset is lifted. GPIO 21
GPIO_Handset = 21

# Pulse Switch for dialing mechanism
GPIO_Dial = 16

PI_HIGH = 1
PI_LOW = 0

# GLobal State Variables
phone_off_hook = False

# Count the pulses
pulse_count = 0
last_tick = 0  # The last time the pulse was detected

# Import the pigpio library for the rotary pulses. The standard GPIO Python library isn't fast enough to detect the pulses
import pigpio

# PiGPIO library instance, globally defined
pi = pigpio.pi()

# Import the time library to allow for delays
import time

# We communicate with the DF Player Pro via Serial Port. Import the serial library
import serial


# Initialise GPIO Pins

pi.set_mode(GPIO_Handset, pigpio.INPUT)
pi.set_pull_up_down(
    GPIO_Handset, pigpio.PUD_UP
)  # Set the pull up resistor on the off_hook PIN

pi.set_mode(GPIO_Dial, pigpio.INPUT)
pi.set_pull_up_down(
    GPIO_Dial, pigpio.PUD_UP
)  # Set the pull up resistor on the dial_pulse PIN
#

# Initialize the serial port for the DF Player Pro
# Open the serial port
audio_serial = serial.Serial("/dev/ttyS0", 115200, timeout=1)

# Send the AT command to initialize the DF Player Pro. Must have \r\n at the end
audio_serial.write("AT+PLAYMODE=3\r\n".encode())
print(f"Sent: AT+PLAYMODE=3")
audio_serial.write("AT+VOL=5\r\n".encode())
print(f"Sent: AT+VOL=5")
# sleep for 1 second to allow the DF Player Pro to respond
time.sleep(1)
print(f"Received: {audio_serial.readline().decode()}")


# Function to play the audio file. The audio file is passed as a parameter, 0-9 for the numbers
def play_audio(file_number):
    global audio_serial

    print(f"Received: {audio_serial.readline().decode()}")
    # Start by playing the ringtone
    audio_serial.write("AT+PLAYFILE=/ringringbetter.wav\r\n".encode())
    time.sleep(2)
    print(f"Received: {audio_serial.readline().decode()}")
    # Send the AT command to play the dialed number
    audio_serial.write(f"AT+PLAYFILE=/{file_number}.wav\r\n".encode())
    print(f"Sent: AT+PLAYFILE=/{file_number}.wav")


def play_dialtone():
    global audio_serial
    # Start by playing the dialtone
    audio_serial.write("AT+PLAYFILE=/dialtone.wav\r\n".encode())
    print(f"Received: {audio_serial.readline().decode()}")


def stop_audio():
    global audio_serial
    # This won't work as I don't know if the audio is playing or not. Need to add silence.wav
    audio_serial.write("AT+PLAY=PP\r\n".encode())
    print(f"Sent: AT+PLAY=PP")
    print(f"Received: {audio_serial.readline().decode()}")


def off_hook_callback(GPIO_Channel, event, tick):
    global phone_off_hook
    global pulse_count
    # Check if the phone is off the hook or on the hook
    if event == 0 and phone_off_hook == False:
        #  = change to low (a falling edge) which means the phone is off the hook and in someones hand.
        print(GPIO_Channel, "Phone Handset has been picked up")
        play_dialtone()
        phone_off_hook = True
        # start_phone_workflow()


def dial_monitor(GPIO_Channel, event, tick):
    """
    The user supplied callback receives three parameters, the GPIO, the level, and the tick.
    Parameter   Value    Meaning
    GPIO        0-31     The GPIO which has changed state
    level       0-2      0 = change to low (a falling edge)
                         1 = change to high (a rising edge)
                         2 = no level change (a watchdog timeout)
    tick        32 bit   The number of microseconds since boot
                         WARNING: this wraps around from
                         4294967295 to 0 roughly every 72 minutes
    """
    global pulse_count, last_tick, phone_off_hook
    # We only care about the pulses when the phone is off the hook.
    if phone_off_hook == False:
        return
    # Check if the pulse is too fast
    if tick - last_tick < 105000:  # 105ms
        return
    last_tick = tick
    pulse_count += 1
    print(GPIO_Channel, event, tick, pulse_count, " Dial Event Detected")


cb_counter_handler = pi.callback(
    GPIO_Dial, pigpio.FALLING_EDGE, dial_monitor
)  # Set the callback for the dial_pulse PIN.
# The off hook callback is unreliable due to the old contacts on the phone. Only checking pick up the pho. Volts to 0.
cb_off_hook_handler = pi.callback(
    GPIO_Handset, pigpio.FALLING_EDGE, off_hook_callback
)  # Set the callback for the off_hook PIN.

# Main Loop
try:
    while True:
        if phone_off_hook == False and pi.read(GPIO_Handset) == PI_LOW:
            # Althought this should have been detected from the event handler, we double check here.
            print("Handset has been picked up")
            phone_off_hook = True
            play_dialtone()
        if phone_off_hook == True and pi.read(GPIO_Handset) == PI_HIGH:
            print("Handset has been put down")
            stop_audio()
            phone_off_hook = False
            pulse_count = 0
        elif phone_off_hook == True:
            # Phone is off hook, dialtone is playing, listen for the pulses, but we need to wait for the pulses to stop before playing the audio

            # Check if the pulse count is greater than 0
            if pulse_count > 0 and last_tick - time.time() > 1:
                print(f"Pulse Count: {pulse_count}")
                # Play the audio file for the number dialed
                play_audio(pulse_count)
                pulse_count = 0
        time.sleep(0.2)

# Not sure we will get here, but to be safe:
# Close the serial port
finally:
    audio_serial.close()
    pi.stop()
    print("Serial Port Closed")
    print("PiGPIO Stopped")
    print("Exiting")
    exit(0)
