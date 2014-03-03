#!/usr/bin/python2

baudrate=115200

import serial
import time
import struct
import sys
import os
import logging
import logging.handlers
from datetime import datetime
from timedrotatingshithandler import TimedRotatingShitHandler

print("Starting...");

LOG_FILENAME = '/home/root/logs/bats/flederlog.txt'

logger = logging.getLogger('MyLogger')
logger.setLevel(logging.INFO)

handler = TimedRotatingShitHandler(LOG_FILENAME, hour=12, minute=0, delay=False, backupCount=60)
formatter = logging.Formatter("%(asctime)s - %(message)s")

handler.setFormatter(formatter)
logger.addHandler(handler);

def setDTR(state):
    if state == 1:
        os.system("echo 1 > /sys/class/gpio/gpio9/value")
    else:
        os.system("echo 0 > /sys/class/gpio/gpio9/value")

setDTR(0)
time.sleep(1)

ser = serial.Serial('/dev/ttyO4', baudrate, xonxoff=0, rtscts=0)

init_time_system = 0
init_time_arduino = 0
init_time_relative = 0
running = 0

def now(arduino):
    global init_time_system,init_time_arduino,init_time_relative,running,init_time_sys
    init_time_sys = int(datetime.now().strftime("%s")) * 1000000
    init_time_arduino = arduino
    init_time_relative = init_time_sys - init_time_arduino
    running = 1
    #print(init_time_sys, '-', init_time_arduino, '=', init_time_relative)

print("Done.");

def got_stupid_data(msg):
    global init_time_system,init_time_arduino,init_time_relative,running,init_time_sys,ser,baudrate
    init_time_relative = 0
    init_time_arduino = 0
    init_time_sys = 0
    running = 0
    logger.info("Got stupid data (%s), resetting Arduino" % msg);
    setDTR(0)
    time.sleep(1)
    ser.close()
    ser = serial.Serial('/dev/ttyO4', baudrate, xonxoff=0, rtscts=0)
    setDTR(1)

setDTR(1)

_data_length = 9
_time_length = 4
_packet_length = 14

def bin(s):
    return str(s) if s<=1 else bin(s>>1) + str(s&1)

def _read():
    byte = ser.read(1)
    return byte

def seek_to_start():
    global _packet_length
    while True:
        if _read() == 'S':
            if _read() == '.':
                if _read() == '.':
                    if _read() == '.':
                        if _read() == '.':
                            len = ord(_read())
                            if len == _packet_length:
                                return True

def check_end():
    if _read() != '.':
        return False
    if _read() != '.':
        return False
    if _read() != '.':
        return False
    if _read() != '.':
        return False
    if _read() != 'E':
        return False
    return True

def got_data(data, timestamp, seperator):
    output = str()
    for i in range(0, _data_length):
        output += bin(ord(data[i])).zfill(8)
    output=output[:-4]
    ftime = init_time_relative + timestamp
    logger.info("%s %d %s" % (seperator,ftime,output));

while ser:
    seek_to_start()
    data = str()
    for i in range(0, _data_length):
        data += _read()
    seperator = _read()
    if seperator == 'T' or seperator == 'I':
        timebytes = str()
        for i in range(0, _time_length):
            timebytes += _read()
        timedata = struct.unpack("=i", timebytes)
        timestamp = timedata[0]
        if seperator == 'I':
            now(timestamp)
        elif not running:
            got_stupid_data("system not running")
        if check_end():
            got_data(struct.unpack("=%ic" % (_data_length), data), timestamp, seperator)
        else:
            got_stupid_data("failed at end")
    else:
        got_stupid_data("failed at seperator")
