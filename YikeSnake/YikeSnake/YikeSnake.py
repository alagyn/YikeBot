# YikeSnake.py
import os

import discord
import consts
import re

from dotenv import load_dotenv

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
users = {}

class Bot(discord.Client):
    
    async def on_ready(self):
        print(f'{self.user} is logged in')
        for g in self.guilds:
            for m in g.members:
                users.update({m.id : 0})

    async def on_message(self, message):
        if(message.author != self.user):
            content = message.content.split(' ')
            send = message.channel.send
            channel = message.channel
            done = False
            updatedYikes = False
            userFound = False

            if(content[0][0] == '\\'):
                
                #Two operator commands: (cmd + @user)
                if(len(content) == 2):
                    cmd = content[0]
                    
                    print('Got raw ID: ' + content[1])

                    if(re.fullmatch(consts.ID_FORMAT, content[1])):
                        
                        updateId = ''

                        if(content[1][2] == '!'):
                            updateId = content[1][3:-1]
                        else:
                            updateId = content[1][2:-1]
                        
                        print('Searching for id:' + updateId)

                        if(updateId in users):
                            userFound = True
                        else:
                            print('ID not found: "' + updateId + '"')

                        done = True

                        if(userFound):
                            print('Found: ' + updateId)
                            #Add Yike
                            if(re.fullmatch(consts.YIKE_CMD, cmd)):
                                users[updateId] += 1
                                updatedYikes = True
                                
                            #Remove Yike
                            elif(re.fullmatch(consts.UNYIKE_CMD, cmd)):
                                if(users[updateId] > 0):
                                    users[updateId] -= 1
                                    updatedYikes = True
                
                            if(updatedYikes):
                                await send('@' + updateId + '... yikes\nYou now have ' + str(users[updateId]) + ' yikes')
                        else:
                            await send('User: "' + updateId + '" not found')
                    else:
                        print('Raw ID not valid: "' + content[1] + '"')
                if(not done):
                    await send('Invalid Command')

                
bot = Bot()
bot.run(token)
