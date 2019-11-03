# cmdUtils.py

from cmds.Quote import *
from cmds.Yike import *
from cmds.List import *
from utils.adminUtils import *

USAGE = 0
FUNC = 1

cmdList = {
    '_yike': [consts.YIKE_USAGE, yikeCmd],
    '_unyike': [consts.UNYIKE_USAGE, yikeCmd],
    '_quote': [consts.QUOTE_USAGE, createQuote],
    '_getQuote': [consts.GET_QUOTE_USAGE, sendQuotes],
    '_list': [consts.LIST_USAGE, listYikes],
    '_logout': ['', adminLogout]
}


async def sendUsage(send, cmd):
    x = cmdList[cmd][USAGE]
    if x:
        await send("Usage:\n" + cmdList[cmd][USAGE])
    else:
        await send("Invalid command")


def getCmd(cmd: str):
    x = cmdList[cmd]
    if x:
        return x[FUNC]
