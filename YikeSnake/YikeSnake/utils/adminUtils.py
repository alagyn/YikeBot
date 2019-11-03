# adminUtils.py

import sys

import discord

import YikeSnake
from utils.fileIO import *


async def adminLogout(bot: YikeSnake, message: discord.Message):
    if message.author.id == consts.ADMIN_ID:
        writeYikeLog(bot.users)
        print(time.asctime() + ': YikeLog Updated, Logging out')
        await bot.change_presence(status=discord.Status.offline)
        await discord.Client.close(bot)
        sys.exit(0)
