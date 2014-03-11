import urllib2
import os
import time

delay = 180 # seconds => 3 minutes
max_fails = 4 # * 3 minutes => 12 minutes
check_url = "http://pass.telekom.de"
second_check_url = "http://google.de" # just in case pass.telekom.de is down...

cur_fails = 0

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

print("I'M GONNA CHECK FOR DA WEB!")

while True:
    if internet_on():
        cur_fails = 0
    else:
        cur_fails = cur_fails + 1
        if cur_fails > max_fails:
            reconnect()
    time.sleep(delay)
