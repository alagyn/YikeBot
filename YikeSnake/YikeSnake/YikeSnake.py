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
    
    async def userNotFound(channel, name):
        await channel.send('User: "' + name + '" not found')

    async def on_message(self, message):
        if(message.author != self.user):
            content = message.content.split(' ')
            send = message.channel.send
            channel = message.channel
            done = False
            updatedYikes = False
            userFound = False

            if(len(content) == 2):
                cmd = content[0]
                name = content[1]
                

                #Add Yike
                if(cmd == consts.YIKE_CMD):
                    if(name in users):
                        users[name] += 1
                        userFound = True
                        updatedYikes = True
                        
                    done = True
                    
                #Remove Yike
                elif(cmd == consts.UNYIKE_CMD):
                    if(name in users):
                        if(users[name] > 0):
                            users[name] -= 1
                            updatedYikes = True
                            userFound = True

                    done = True
                
                if(updatedYikes):
                    await send(name + '... yikes\nYou now have ' + str(users[name]) + ' yikes')
                if(not userFound):
                    userNotFound(channel, name)

            if(not done):
                await send('Invalid Command')

                
bot = Bot()
bot.run(token)
