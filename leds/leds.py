import os
import time

def check_led1():
    try:
        if os.system("""if [ "$(systemctl status bats | grep Active | awk '{print $2}')" == "active" ]; then exit 0; else exit 1; fi""") == 0:
            return True
        else:
            return False
    except:
        return False

def check_led2():
    try:
        if os.system("""ping -c1 -s0 -w1 vpn.kurz.pw > /dev/null""") == 0:
            return True
        else:
            return False
    except:
        return False

def check_led3():
    try:
        if os.system("""ping -c1 -s0 -w1 10.8.0.1 > /dev/null""") == 0:
            return True
        else:
            return False
    except:
        return False

def setup_leds():
    os.system("""echo heartbeat > /sys/class/leds/beaglebone\:green\:usr0/trigger""")
    os.system("""echo none > /sys/class/leds/beaglebone\:green\:usr1/trigger""")
    os.system("""echo none > /sys/class/leds/beaglebone\:green\:usr2/trigger""")
    os.system("""echo none > /sys/class/leds/beaglebone\:green\:usr3/trigger""")

def set_led(led,value):
    try:
        if value:
            print led,value
            os.system("""cat /sys/class/leds/beaglebone\:green\:usr%s/max_brightness > /sys/class/leds/beaglebone\:green\:usr%s/brightness""" % (led,led))
        else:
            os.system("""echo 0 > /sys/class/leds/beaglebone\:green\:usr%s/brightness""" % (led))
    except:
        pass

while True:
    try:
        print "check 1"
        set_led(1,check_led1())
        print "check 2"
        set_led(2,check_led2())
        print "check 3"
        set_led(3,check_led3())
        time.sleep(30)
    except:
        pass
