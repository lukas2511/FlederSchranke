import time
import datetime
import errno, logging, socket, os, cPickle, struct, time, re
from logging.handlers import BaseRotatingHandler as BaseRotatingShitHandler
import pytz

class TimedRotatingShitHandler(BaseRotatingShitHandler):
    def __init__(self, filename, hour=12, minute=0, backupCount=0, encoding=None, delay=False, utc=False):
        BaseRotatingShitHandler.__init__(self, filename, 'a', encoding, delay)

        self.delay = delay
        self.backupCount = backupCount
        self.utc = utc

        self.interval = 60 * 60 * 24
        self.suffix = "%Y-%m-%d"
        self.extMatch = r"^\d{4}-\d{2}-\d{2}$"
        self.extMatch = re.compile(self.extMatch)

        t = int(time.mktime(datetime.datetime.now(pytz.timezone("Europe/Berlin")).replace(hour=hour, minute=minute, second=0).timetuple()))
        if datetime.datetime.now(pytz.timezone("Europe/Berlin")).hour < hour or (datetime.datetime.now(pytz.timezone("Europe/Berlin")).hour==hour and datetime.datetime.now(pytz.timezone("Europe/Berlin")).minute < minute):
            self.rolloverAt = self.computeRollover(t-self.interval)
        else:
            self.rolloverAt = self.computeRollover(t)

    def computeRollover(self, currentTime):
        result = currentTime + self.interval
        return result

    def shouldRollover(self, record):
        t = int(time.time())
        if t >= self.rolloverAt:
            return 1
        return 0

    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None
        currentTime = int(time.time())
        dstNow = time.localtime(currentTime)[-1]
        t = self.rolloverAt - self.interval
        if self.utc:
            timeTuple = time.gmtime(t)
        else:
            timeTuple = time.localtime(t)
            dstThen = timeTuple[-1]
            if dstNow != dstThen:
                if dstNow:
                    addend = 3600
                else:
                    addend = -3600
                timeTuple = time.localtime(t + addend)
        dfn = self.baseFilename + "." + time.strftime(self.suffix, timeTuple)
        if os.path.exists(dfn):
            os.remove(dfn)
        if os.path.exists(self.baseFilename):
            os.rename(self.baseFilename, dfn)
        if not self.delay:
            self.stream = self._open()
        newRolloverAt = self.computeRollover(currentTime)
        while newRolloverAt <= currentTime:
            newRolloverAt = newRolloverAt + self.interval
        self.rolloverAt = newRolloverAt
