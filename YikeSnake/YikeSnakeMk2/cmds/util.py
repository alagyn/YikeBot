# util.py

from discord.ext import commands
import typing
import discord

CLEAR_USAGE = 'Clears the last message sent by the bot'


class Util(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command(name="clear", help=CLEAR_USAGE, brief="_clear")
    async def clear(self, ctx):
        if self.bot.lastMessage is not None:
            m2 = discord.utils.get(self.bot.cached_messages, id=self.bot.lastCmd)
            for x in self.bot.lastMessage:
                m: discord.Message = discord.utils.get(self.bot.cached_messages, id=x)
                await m.delete()
            await ctx.message.delete()
            await m2.delete()
            self.bot.lastMessage = None


def setup(bot):
    bot.add_cog(Util(bot))