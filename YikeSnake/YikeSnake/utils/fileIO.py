# fileIO.py

from utils.timeUtils import *
import consts
import json


def readYikeLog(users):
    try:
        with open(consts.LOG) as f:
            for line in f:
                data = line.split(":")
                users.update({data[0]: int(data[1])})
    except OSError:
        print(time.asctime() + ": Error reading yike log")


def writeYikeLog(users):
    try:
        with open(consts.LOG, 'w') as f:
            for userId in users:
                f.write(userId + ":" + str(users[userId]) + "\n")
    except OSError:
        print(time.asctime() + ": Error writing yike log")


def writeQuote(subject, quote):
    try:
        with open(consts.QUOTES, mode="a") as f:
            out = ''
            for x in quote:
                out += x + " "

            curTime = getCurrentTime()
            f.write(json.dumps([subject, curTime, out]) + '\n')
    except OSError:
        print(time.asctime() + ": Error writing quote")


def getQuotes(userId):
    try:
        with open(consts.QUOTES, mode='r') as f:
            out = ''
            for line in f:
                quote = json.loads(line)
                if quote[0] == userId:
                    out += ' ' + readDate(quote[1]) + '\n' + quote[2] + '\n\n'

            return out
    except OSError:
        print(time.asctime() + ': Error reading quotes')


def getGuildQuotes(guild):
    try:
        with open(consts.QUOTES, mode='r') as f:
            out = ''
            for line in f:
                quote = json.loads(line)

                for m in guild.members:
                    if str(m.id) == quote[0]:
                        name: str
                        if m.nick is not None:
                            name = m.nick
                        else:
                            name = m.name

                        out += name + ' ' + readDate(quote[1]) + '\n' + quote[2] + '\n\n'
                        break
            return out
    except OSError:
        print(time.asctime() + ': Error reading quotes')
