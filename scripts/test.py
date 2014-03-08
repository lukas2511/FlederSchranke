from datetime import datetime
import curses
import os
import struct
import time
import sys
import serial

baudrate = 115200
lftime = "0"
input = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

def getTerminalSize():
    import os
    env = os.environ
    def ioctl_GWINSZ(fd):
        try:
            import fcntl, termios, struct, os
            cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ,
        '1234'))
        except:
            return
        return cr
    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        cr = (env.get('LINES', 25), env.get('COLUMNS', 80))

        ### Use get(key[, default]) instead of a try/catch
        #try:
        #    cr = (env['LINES'], env['COLUMNS'])
        #except:
        #    cr = (25, 80)
    return int(cr[1]), int(cr[0])

stdscr = curses.initscr()
curses.start_color()
curses.noecho()
curses.cbreak()

(width, height) = getTerminalSize()
win = curses.newwin(height, width, 0, 0)

curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_GREEN)
curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_RED)
curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

p=0
for x in range(0,7):
    for y in range(x*10,x*10+11):
        if p<68:
            stdscr.addstr((y-x*10)*2+2,x*9+1," %s " % str(p).rjust(2), curses.color_pair(3))
            p=p+1

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

def got_stupid_data(msg):
    global init_time_system,init_time_arduino,init_time_relative,running,init_time_sys,ser,baudrate
    init_time_relative = 0
    init_time_arduino = 0
    init_time_sys = 0
    running = 0
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

def init_screen():
    p=0
    for x in range(0,7):
        for y in range(x*10,x*10+11):
            if p<68:
                if input[p]:
                    stdscr.addstr((y-x*10)*2+2,x*9+6," ON", curses.color_pair(2))
                else:
                    stdscr.addstr((y-x*10)*2+2,x*9+6,"OFF", curses.color_pair(1))
                p=p+1
    date = str(datetime.now())
    stdscr.addstr(0,width-1-len(date),date)
    stdscr.addstr(0,1,lftime)
    stdscr.refresh()

def got_data(data, timestamp, seperator):
    global input,lftime
    output = str()
    for i in range(0, _data_length):
        output += bin(ord(data[i])).zfill(8)
    output=output[:-4]
    ftime = init_time_relative + timestamp
    input = [ int(x) for x in output ]
    lftime = str(ftime)
    p=0
    off=0
    for x in range(0,7):
        for y in range(x*10,x*10+11):
            if p<68:
                if input[p]:
                    stdscr.addstr((y-x*10)*2+2,x*9+6," ON", curses.color_pair(2))
                else:
                    stdscr.addstr((y-x*10)*2+2,x*9+6,"OFF", curses.color_pair(1))
                    off=off+1
                p=p+1
    date = str(datetime.now())
    stdscr.addstr(0,width-1-len(date),date)
    stdscr.addstr(0,1,lftime)
    stdscr.addstr(0,20,str(off))
    stdscr.refresh()

init_screen()

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


while True:
    time.sleep(10)
