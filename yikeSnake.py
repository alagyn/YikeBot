# yikeSnake.py
import discord
from discord.ext import commands

from utils import timeUtils
import sys

from consts import ERROR_OUTPUT_MESSAGE


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
        self.previousMessages = []
        self.lastCmd: int = 0

    def addAdminLog(self, message: str):
        output = f'{timeUtils.readDate(timeUtils.getCurrentTime())}: {message}'
        if self.outputFile is not None:
            with open(self.outputFile, mode='a') as log:
                log.write(f'{output}\n')
        else:
            print(output)

    def setPreviousMsgs(self, msgs: [], ctx):
        self.previousMessages = []
        self.lastCmd = ctx.message.id
        for x in msgs:
            self.previousMessages.append(x.id)

    async def on_member_join(self, member):
        pass

    async def on_ready(self):
        self.addAdminLog(f'{self.user} is logged in')
        activity = discord.Activity(name='_help', type=discord.ActivityType.watching)
        await self.change_presence(activity=activity)

    async def on_command_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(str(error))
        elif not isinstance(error, commands.UserInputError):
            self.previousMessages = [await ctx.send(ERROR_OUTPUT_MESSAGE)]
            print(f'{error}\n\t{ctx.message.content}', file=sys.stderr)

    @staticmethod
    async def on_command(ctx: commands.Context):
        pass
