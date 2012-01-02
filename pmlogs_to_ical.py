#!/usr/bin/env python

"""
Create a calendar of wake-sleep sessions based on power management logs.

$ sudo pmset -g log > /tmp/pmlog.txt
$ python pmlogs_to_ical.py /tmp/pmlog.txt > ~/Desktop/pmlog.ics
"""

import sys
from datetime import datetime
import uuid

def datetime_from_pm_line(line):

    parts = line.split(' ')
    date_string = parts[3]
    time_string = parts[4]
    am_pm_string = parts[5]
    
    s = ' '.join((date_string, time_string, am_pm_string))
    # 1/2/12 12:45:02 AM
    
    return datetime.strptime(s, "%m/%d/%y %I:%M:%S %p")

def formatted_datetime(dt):
    return dt.strftime("%Y%m%dT%H%M%S")

class State:
    UNKNOWN, WAKE, SLEEP, READ_TIME_WAKE, READ_TIME_SLEEP = range(5)

state = State.UNKNOWN
event = None

print "BEGIN:VCALENDAR"
print "PRODID:-//pm_activity.py//seriot.ch//"
print "VERSION:2.0"

for line in open(sys.argv[1]):
    
    if state in (State.UNKNOWN, State.READ_TIME_SLEEP):
        if line.startswith(' * Domain: wake'):
            state = State.WAKE
            print "BEGIN:VEVENT"
            print "SUMMARY:Session"

    elif state in (State.UNKNOWN, State.READ_TIME_WAKE):
        if line.startswith(' * Domain: sleep'):
            state = State.SLEEP
            
    elif state == State.WAKE:
        if line.startswith(' - Time: '):
            state = State.READ_TIME_WAKE
            date_start = datetime_from_pm_line(line)
            print "UID:%s-pm_activity.py" % date_start #str(uuid.uuid4())
            print "DTSTART:%s" % formatted_datetime(date_start)

    elif state == State.SLEEP:
        if line.startswith(' - Time: '):
            state = State.READ_TIME_SLEEP
            date_stop = datetime_from_pm_line(line)
            print "DTEND:%s" % formatted_datetime(date_stop)
            print "END:VEVENT"

# end of current event
if state == State.READ_TIME_WAKE:
    state = State.READ_TIME_SLEEP
    print "DTEND:%s" % formatted_datetime(datetime.now())
    print "END:VEVENT"

print "END:VCALENDAR"
