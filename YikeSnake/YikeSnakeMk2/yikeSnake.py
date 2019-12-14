# yikeSnake.py
import discord
from discord.ext import commands

from utils import timeUtils
import sys


class YikeSnake(discord.ext.commands.Bot):

    def __init__(self, logFile, waitTime):
        super().__init__(command_prefix='_', case_insensitive=True)

        startTime = timeUtils.readDate(timeUtils.getCurrentTime())
        if logFile is not None:
            with open(logFile, mode='w') as f:
                f.write(f'Log Init at {startTime}\n')
        print(f"Error log init at {startTime}", file=sys.stderr)
        self.outputFile = logFile
        self.waitTime = waitTime
        self.lastMessage = []
        self.lastCmd: int

    def addAdminLog(self, message: str):
        output = f'{timeUtils.readDate(timeUtils.getCurrentTime())}: {message}'
        if self.outputFile is not None:
            with open(self.outputFile, mode='a') as log:
                log.write(f'{output}\n')
        else:
            print(output)

    async def on_member_join(self, member):
        pass

    async def on_ready(self):
        self.addAdminLog(f'{self.user} is logged in')
        await self.change_presence(activity=discord.Game("_help"))

    async def on_command_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(error)
