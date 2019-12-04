# util.py

from discord.ext import commands
import typing
import discord


class Util(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    # TODO Clear usage

    @commands.command(name="clear")
    async def clear(self, ctx):
        if self.bot.lastMessage is not None:
            m: discord.Message = discord.utils.get(self.bot.cached_messages, id=self.bot.lastMessage)
            m2 = discord.utils.get(self.bot.cached_messages, id=self.bot.lastCmd)
            await m.delete()
            await ctx.message.delete()
            await m2.delete()
            self.bot.lastMessage = None
