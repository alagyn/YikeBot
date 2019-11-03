# YikeSnake.py
import os

from cmds.List import *
from cmds.Quote import *

import discord
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('DISCORD_TOKEN')


class YikeSnake(discord.Client):
    users = {}

    async def on_ready(self):
        print(time.asctime() + ": " + f'{self.user} is logged in')
        for g in self.guilds:
            for m in g.members:
                self.users.update({str(m.id): 0})
        readYikeLog(self.users)
        game = discord.Game("_help")
        await self.change_presence(status=discord.Status.online, activity=game)

    async def on_message(self, message):
        if message.author != self.user:
            content = message.content.split(' ')
            send = message.channel.send

            if len(content) > 0 and len(content[0]) > 0 and content[0][0] == '_':

                cmd = content[0]
                cmdFunc = getCmd(cmd)

                if cmdFunc:
                    cmdFunc(bot=bot, send=send, message=message, content=content)
                else:
                    await send('Invalid Command: Try _help')


bot = YikeSnake()
bot.run(token)
