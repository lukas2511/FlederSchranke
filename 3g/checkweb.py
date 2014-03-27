import urllib2
import os
import time
import datetime

delay = 180 # seconds => 3 minutes
max_fails = 4 # * 3 minutes => 12 minutes
max_hard_fails = 960 # * 3 minutes => 2 days

check_url = "http://pass.telekom.de"
second_check_url = "http://google.de" # just in case pass.telekom.de is down...

cur_fails = 0
cur_hard_fails = 0

def internet_on():
    global check_url
    try:
        response=urllib2.urlopen(check_url,timeout=3)
        return True
    except:
        try:
            response=urllib2.urlopen(second_check_url,timeout=3)
            return True
        except:
            pass
    return False

def reconnect():
    try:
        os.system("/home/root/lichtschranke/3g/sakis3g disconnect")
        cur_fails = 0
        time.sleep(60)
    except:
        pass

def rebootmaybe():
    curhour = datetime.datetime.now().hour
    if curhour > 8 and curhour < 17:
        os.system("reboot")

print("I'M GONNA CHECK FOR DA WEB!")

while True:
    if internet_on():
        cur_fails = 0
        cur_hard_fails = 0
    else:
        cur_fails += 1
        cur_hard_fails += 1
        if cur_fails > max_fails:
            reconnect()
        if cur_hard_fails > max_hard_fails:
            rebootmaybe()
    time.sleep(delay)
