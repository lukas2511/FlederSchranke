#!/usr/bin/python2

import serial
import time
import sys
import logging
import logging.handlers
from datetime import datetime
from timedrotatingshithandler import TimedRotatingShitHandler
print("Starting...");

LOG_FILENAME = '/home/root/logs/weather/weatherlog.txt'

logger = logging.getLogger('MyLogger')
logger.setLevel(logging.INFO)

handler = TimedRotatingShitHandler(LOG_FILENAME, hour=12, minute=0, backupCount=60, delay=False)
formatter = logging.Formatter("%(asctime)s - %(message)s")

handler.setFormatter(formatter)
logger.addHandler(handler);

ser = serial.Serial('/dev/ttyO5', 9600)

time.sleep(1)

print("Done.");

while ser:
	line = ser.readline().decode('ascii').rstrip()
	logger.info(line)
