#!/usr/bin/python3
# This script is used to test the serial port for DF Player Pro and send AT commands to it.

SERIAL_PORT = "/dev/ttyS0"
BAUD_RATE = 115200

AT_INIT = "AT+PLAYMODE=3"  # play one song and pause
AT_PLAY = "AT+PLAYFILE="  # Append the filename ie 0.WAV
AT_VOL = "AT+VOL=5"  # Set the volume to 5
AT_END = "\r\n"

import sys
import os
import time

import serial


def main():
    # Open the serial port
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

    # Send the AT command to initialize the DF Player Pro
    ser.write(AT_INIT.encode() + AT_END.encode())
    # wait for the response from the DF Player Pro
    print(f"Sent: {AT_INIT}")
    # sleep for 1 second to allow the DF Player Pro to respond
    time.sleep(1)
    print(f"Received: {ser.readline().decode()}")

    # Send the AT command to set the volume
    ser.write(AT_VOL.encode() + AT_END.encode())
    time.sleep(1)

    print(f"Sent: {AT_VOL}")
    print(f"Received: {ser.readline().decode()}")

    # Send the AT command to play the file
    ser.write(AT_PLAY.encode() + "1.wav".encode() + AT_END.encode())
    time.sleep(1)
    print(f"Sent: {AT_PLAY}1.wav")
    print(f"Received: {ser.readline().decode()}")
    time.sleep(5)

    # Close the serial port
    ser.close()


if __name__ == "__main__":
    main()
