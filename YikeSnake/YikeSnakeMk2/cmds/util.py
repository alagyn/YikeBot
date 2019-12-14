# util.py

from discord.ext import commands
import discord

import yikeSnake

CLEAR_USAGE = 'Clears the last message sent by the bot'


class Util(commands.Cog):

    def __init__(self, bot: yikeSnake.YikeSnake):
        self.bot = bot
        self._last_member = None

    @commands.command(name="clear", help=CLEAR_USAGE, brief="_clear")
    async def clear(self, ctx):
        await ctx.message.delete()
        if self.bot.lastMessage is not None:
            m2 = discord.utils.get(self.bot.cached_messages, id=self.bot.lastCmd)
            for x in self.bot.lastMessage:
                m: discord.Message = discord.utils.get(self.bot.cached_messages, id=x)
                await m.delete()
            await m2.delete()
            self.bot.lastMessage = None


def setup(bot):
    bot.add_cog(Util(bot))
