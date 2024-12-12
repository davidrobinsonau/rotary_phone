#!/bin/sh

# This script will start the Python script and restart it if it crashes
cd /home/phone/rotary_phone
# Move the log file so that we don't fill up all space.
mv log_2.txt log_3.txt
mv log_1.txt log_2.txt
mv log.txt log_1.txt

# Start the script

while true; do
    /home/phone/rotary_phone/monitorv2.py >> log.txt 2>&1
    sleep 10
done