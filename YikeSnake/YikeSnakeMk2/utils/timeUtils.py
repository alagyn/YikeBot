# timeUtils.py

import time


def getCurrentTime():
    curTime = time.localtime()
    timeList = [curTime.tm_year, curTime.tm_mon, curTime.tm_mday,
                curTime.tm_wday, curTime.tm_hour, curTime.tm_min]
    return timeList


def readDate(date):
    year = date[0]
    month = date[1]
    mday = date[2]

    if date[3] is 0:
        wday = "Mon"
    elif date[3] is 1:
        wday = "Tue"
    elif date[3] is 2:
        wday = "Wed"
    elif date[3] is 3:
        wday = "Thu"
    elif date[3] is 4:
        wday = "Fri"
    elif date[3] is 5:
        wday = "Sat"
    else:
        wday = "Sun"

    hour = date[4]
    minute = date[5]

    return f'( {wday} {month}/{mday}/{year % 1000} {hour}:{minute} )'