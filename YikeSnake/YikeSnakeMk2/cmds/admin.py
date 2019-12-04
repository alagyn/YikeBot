# admin.py

from discord.ext import commands
import discord
from sys import exit


class Admin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command(name='logout', hidden=True)
    @commands.is_owner()
    async def logoutCmd(self, ctx):
        # TODO fileIO.writeYikeLog(self.addOutputLog, self.users)
        self.bot.addAdminLog('YikeLog Updated, Logging out')
        await ctx.message.delete()
        await self.bot.change_presence(status=discord.Status.offline)
        await discord.Client.close(self.bot)
        exit(0)
