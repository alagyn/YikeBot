# YikeSnake.py
import os

import discord
import consts

from dotenv import load_dotenv

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
users = {}

class Bot(discord.Client):
    
    async def on_ready(self):
        print(f'{self.user} is logged in')

    async def on_message(self, message):
        if(message.author != self.user):
            content = message.content.split(' ')
            
            if(len(content) == 2):
                cmd = content[0]
                if(cmd == consts.CMD):
                    name = content[1]
                
                    if(name in users):
                        users[name] += 1
                    else:
                        users.update({name : 1} )
                
                    await message.channel.send(name + '... yikes\nYou now have ' + str(users[name]) + ' yikes')
            else:
                await message.channel.send('Invalid Command')
                
bot = Bot()
bot.run(token)
