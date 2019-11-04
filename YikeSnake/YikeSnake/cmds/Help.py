# Help.py
from consts import USAGE


async def helpOutput(bot, send, message=None, content=None):
    output = ''
    cmdList = bot.cmdList
    for x in cmdList:
        output += cmdList[x][USAGE]
    await send(output)
