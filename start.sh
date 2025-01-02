#!/bin/sh

# Check that we are being run on the tty console
if [ $(tty) != "/dev/tty1" ]; then
    echo "Skipping startup script because we are not on tty1"
    exit 1
fi


# This script will start the Python script and restart it if it crashes
cd /home/phone/rotary_phone
# Move the log file so that we don't fill up all space.
mv log_2.txt log_3.txt
mv log_1.txt log_2.txt
mv log.txt log_1.txt

# Start the script

while true; do
    # Tee is used to output to the terminal and to a file
    /home/phone/rotary_phone/monitorv2.py 2>&1 | tee -a log.txt
    sleep 10
done