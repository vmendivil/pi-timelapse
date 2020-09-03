from datetime import datetime
import os
import sys

d = datetime.now()
print ("Now: {}".format(d))
f = d.strftime('%Y%m%d%H%M%S')
print ("Format: {}".format(f))
t = d.timetz()
print ("Time: {}".format(t))
h = t.hour
print ("Hour: {}".format(h))
m = t.minute
print ("Minute: {}".format(m))

# Format must be 24 hrs
enableTimeframe = True
startHour = 6
startMinute = 30
endHour = 20
endMinute = 0

def isLapseTimeValid():
    now = datetime.now().timetz()

    def isStartTimeValid():
        if startHour == now.hour:
            return startMinute <= now.minute
        else:
            return startHour < now.hour

    def isEndTimeValid():
        if now.hour == endHour:
            return now.minute <= endMinute
        else:
            return now.hour < endHour

    return not enableTimeframe or (enableTimeframe and isStartTimeValid() and isEndTimeValid())

print ("isLapseTimeValid: {}".format(isLapseTimeValid()))

print (".", end = "")
print (".")

