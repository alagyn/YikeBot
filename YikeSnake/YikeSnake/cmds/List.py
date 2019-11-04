# List.py

import re
from utils.userUtil import *
from consts import ID_FORMAT


async def listYikes(send, bot, message, content):
    # List all
    cmd = content[0]
    users = bot.users

    if len(content) == 1:
        nameList = 'CURRENT YIKE TOTALS:\n'
        for m in message.guild.members:
            # Check for Nickname
            if str(m.nick) != "None":
                name = str(m.nick)
            else:
                name = str(m.name)

            nameList += "\t" + name + ": " + str(users[str(m.id)]) + "\n"
        await send(nameList)
    # list single
    elif len(content) == 2:
        if re.fullmatch(ID_FORMAT, content[1]):
            userId = getId(content[1])
            await send(f'{getName(message.guild, userId)} has {str(users[userId])} yikes')
        else:
            await sendUsage(send, cmd)
    else:
        await sendUsage(send, cmd)
