# YikeSnake.py
import os
import sys
import time
import discord
from utils import fileIO
from dotenv import load_dotenv

from consts import *
from cmds import *

load_dotenv()
token = os.getenv('DISCORD_TOKEN')


# noinspection PyMethodMayBeStatic
class YikeSnake(discord.Client):
    users = {}

    async def adminLogout(self, message: discord.Message):
        if str(message.author.id).__eq__(ADMIN_ID):
            fileIO.writeYikeLog(self.users)
            print(time.asctime() + ': YikeLog Updated, Logging out')
            await self.change_presence(status=discord.Status.offline)
            await discord.Client.close(self)
            sys.exit(0)

    cmdList = dict(_yike=[YIKE_USAGE, Yike.yikeCmd], _unyike=[UNYIKE_USAGE, Yike.yikeCmd],
                   _quote=[QUOTE_USAGE, Quote.createQuote], _getQuotes=[GET_QUOTE_USAGE, Quote.sendQuotes],
                   _list=[LIST_USAGE, List.listYikes], _help=[HELP_USAGE, Help.helpOutput])

    def getCmd(self, cmd: str):
        if cmd in self.cmdList:
            return self.cmdList[cmd][FUNC]
        else:
            return None

    async def sendUsage(self, send, cmd):
        x = self.cmdList[cmd][USAGE]
        if x:
            await send("Usage:\n" + cmdList[cmd][USAGE])
        else:
            await send("Invalid command")

    async def on_ready(self):
        print(time.asctime() + ": " + f'{self.user} is logged in')
        for g in self.guilds:
            for m in g.members:
                self.users.update({str(m.id): 0})
        fileIO.readYikeLog(self.users)
        game = discord.Game("_help")
        await self.change_presence(status=discord.Status.online, activity=game)

    async def on_message(self, message):
        if message.author != self.user:
            content = message.content.split(' ')
            send = message.channel.send

            if len(content) > 0 and len(content[0]) > 0 and content[0][0] == '_':

                cmd = content[0]
                cmdFunc = None
                if cmd.__eq__('_logout'):
                    await self.adminLogout(message)
                else:
                    cmdFunc = self.getCmd(cmd)

                if cmdFunc is not None:
                    await cmdFunc(bot=self, send=send, message=message, content=content)
                else:
                    await send('Invalid Command: Try _help')


curBot = YikeSnake()
curBot.run(token)
