# EchoBot

from dotenv import load_dotenv
import os
from asyncio import sleep
from discord.ext import commands

bot = commands.Bot('?', case_insensitive=True)


@bot.command(name="echo", rest_is_raw=True)
async def echo(ctx, *, arg: str):
    await sleep(2.5)
    await ctx.send(arg.strip())


@bot.command(name="logout")
async def logout(ctx):
    await bot.close()

load_dotenv()
token = os.getenv("DISCORD_TOKEN")
bot.run(token)
