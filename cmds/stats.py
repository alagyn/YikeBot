# stats.py
# Stats for nerds

from discord.ext import commands

import yikeSnake


class Stats(commands.Cog):
    def __init__(self, bot: yikeSnake.YikeSnake):
        self.bot = bot
