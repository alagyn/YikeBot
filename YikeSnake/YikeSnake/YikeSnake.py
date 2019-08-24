# YikeSnake.py
import os

import discord

from dotenv import load_dotenv

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

class Bot(discord.Client):
    
    async def on_ready(self):
        print(f'{self.user} is logged in')

    async def on_message(self, message):
        if(message.author != self.user):
            await message.channel.send(message.content)
        
bot = Bot()
bot.run(token)
