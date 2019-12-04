# quote.py

from discord.ext import commands


class Quote(commands.Cog):

    def __init__(self, bot):
        self.message = None
        self.bot = bot
        self._last_member = None

    # TODO quote usage

    @commands.command(name="quote", rest_is_raw=True)
    async def quote(self, ctx, ):
        # TODO quotes parsing
        pass

