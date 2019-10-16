#!/bin/sh

python3 /home/pi/hotspot.py &
sleep 5
python3 /home/pi/code/portFile_init.py &
sleep 1
python3 /home/pi/code/serial_indoor.py &
sleep 9
python3 /home/pi/code/serial_outdoor.py &
