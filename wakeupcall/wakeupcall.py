import serial
import datetime
import time
from config import number

print number

time.sleep(60) # 60 sekunden warten, stick hat evtl. noch keine verbindung

dongle = serial.Serial(port="/dev/ttyUSB1",baudrate=115200,timeout=0,rtscts=0,xonxoff=0)
 
def sendatcmd(cmd):
    dongle.write('AT'+cmd+'\r')
 
sendatcmd('+CMGF=1')
sendatcmd('+CMGS="%s"' % number)
dongle.write('Hallo, es ist der %s und %s Uhr, und ich bin grade (neu) gestartet.' % (datetime.datetime.now().date().isoformat(), datetime.datetime.now().time().isoformat()))
 
dongle.write(chr(26))
 
dongle.close()

while True:
    time.sleep(60)
