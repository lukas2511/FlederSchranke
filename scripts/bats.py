#!/usr/bin/python2

baudrate=115200
micros_overflow=1810e6

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

handler = TimedRotatingShitHandler(LOG_FILENAME, hour=8, minute=0, delay=False, backupCount=60)
formatter = logging.Formatter("%(asctime)s - %(message)s")

handler.setFormatter(formatter)
logger.addHandler(handler);

def overflowed():
    global init_time_sys,micros_overflow
    if (int(datetime.now().strftime("%s")) * 1000000) > (init_time_sys+micros_overflow):
        return True
    else:
        return False

def setDTR(state):
    if not os.path.exists("/sys/class/gpio/gpio9"):
        os.system("echo 9 > /sys/class/gpio/export")
        os.system("echo out > /sys/class/gpio/gpio9/direction")

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
    output="".join([
        output[7], # A 1
        output[29], # A 2
        output[47], # A 3
        output[45], # A 4
        output[26], # A 5
        output[67], # A 6
        output[49], # A 7
        output[43], # A 8
        output[41], # A 9
        output[11], # A 10
        output[9], # A 11
        output[32], # A 12
        output[15], # A 13
        output[13], # A 14
        output[5], # A 15
        output[63], # A 16
        output[59], # A 17
        output[61], # A 18
        output[57], # A 19
        output[64], # A 20
        output[66], # A 21
        output[23], # A 22
        output[21], # A 23
        output[19], # A 24
        output[17], # A 25

        output[31], # B 1
        output[28], # B 2
        output[46], # B 3
        output[40], # B 4
        output[25], # B 5
        output[27], # B 6
        output[44], # B 7
        output[42], # B 8
        output[10], # B 9
        output[8], # B 10
        output[50], # B 11
        output[48], # B 12
        output[33], # B 13
        output[3], # B 14
        output[52], # B 15
        output[51], # B 16
        output[53], # B 17
        output[55], # B 18
        output[54], # B 19
        output[34], # B 20
        output[35], # B 21
        output[36], # B 22
        output[37], # B 23
        output[39], # B 24
        output[38], # B 25
    ])
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
        elif overflowed():
            got_stupid_data("micros overflowed without notice?")
        if check_end():
            got_data(struct.unpack("=%ic" % (_data_length), data), timestamp, seperator)
        else:
            got_stupid_data("failed at end")
    else:
        got_stupid_data("failed at seperator")
