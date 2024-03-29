# yikeSnake.py
import discord
from discord.ext import commands

from utils import timeUtils
import sys
# import asyncio
import traceback

from consts import ERROR_OUTPUT_MESSAGE


def getLogTimeStr():
    return timeUtils.readDate(timeUtils.getCurrentTime())


class YikeSnake(discord.ext.commands.Bot):

    def __init__(self, logFile, backupFolder, waitTime, backupTime):
        intent = discord.Intents.none()
        intent.members = True
        intent.guilds = True
        intent.guild_messages = True
        intent.guild_reactions = True
        intent.emojis = True
        intent.voice_states = True
        super().__init__(command_prefix='_', case_insensitive=True, intents=intent)

        startTime = timeUtils.readDate(timeUtils.getCurrentTime())
        if logFile is not None:
            with open(logFile, mode='w') as f:
                f.write(f'Log Init at {startTime}\n')
        print(f"Error log init at {startTime}", file=sys.stderr)
        self.outputFile = logFile
        self.waitTime = waitTime
        self.previousMessages = []
        self.lastCmd: int = 0
        self.backupFolder = backupFolder
        self.backupTime = backupTime
        self.needToExit = False

    def addAdminLog(self, message: str):
        output = f'{getLogTimeStr()}: {message}'
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
        # Intentionally left blank
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
            tb = traceback.TracebackException.from_exception(error).format()
            tb = ''.join(tb)
            print(f'{getLogTimeStr()}:\n\t{error}\n\t{ctx.message.content}\n{tb}', file=sys.stderr)

    @staticmethod
    async def on_command(ctx: commands.Context):
        pass

    async def on_command_completion(self, ctx: commands.Context):
        pass
