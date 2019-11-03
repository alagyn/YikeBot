# Quote.py

from utils.cmdUtils import *
from utils.userUtil import *
from utils.fileIO import *

import re
import discord


async def createQuote(send, content):
    err = False
    cmd = content[0]

    if len(content) < 3:
        err = True
        await sendUsage(send, cmd)

    if not err:
        subject = getId(content[1])
        writeQuote(subject, content[2:])
        await send("Quote Recorded")


async def sendQuotes(send, message: discord.Message, content):
    err = False
    cmd = content[0]

    if len(content) > 2:
        err = True
        await sendUsage(send, cmd)

    if not err:
        if len(content) > 1 and re.fullmatch(consts.ID_FORMAT, content[1]):
            dat = getQuotes(getId(content[1]))
        else:
            dat = getGuildQuotes(message.guild)

        with open(consts.Q_OUTPUT, mode='w') as f:
            f.write(dat)
        with open(consts.Q_OUTPUT, mode='rb') as f:
            await send(file=discord.File(f, filename='quotes.txt'))
