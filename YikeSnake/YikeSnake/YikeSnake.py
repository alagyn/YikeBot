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
                users.update({str(m.id) : 0})

        game = discord.Game("_help")
        await self.change_presence(status=discord.Status.online, activity=game)

    async def on_message(self, message):
        if(message.author != self.user):
            content = message.content.split(' ')
            send = message.channel.send
            channel = message.channel
            userFound = False

            if(len(content) > 0 and len(content[0]) > 0 and content[0][0] == '_'):
                
                #Two operator commands: (cmd + @user)
                
                cmd = content[0]
                
                #Update Yikes
                if(re.fullmatch(consts.YIKE_CMD, cmd) or re.fullmatch(consts.UNYIKE_CMD, cmd)):
                    
                    done = False

                    if(len(content) != 2 or not re.fullmatch(consts.ID_FORMAT, content[1])):
                        await send('Usage:\n_yike @user')
                        done = True
                    
                    if(not done):
                        deltaYike = 0
                        
                        if(re.fullmatch(consts.YIKE_CMD, cmd)):
                            deltaYike = 1
                        else:
                            deltaYike = -1

                        updateId = ''

                        if(content[1][2] == '!'):
                            updateId = content[1][3:-1]
                        else:
                            updateId = content[1][2:-1]

                        if(updateId in users):
                            users[updateId] += deltaYike

                            update = True

                            if(users[updateId] < 0):
                                users[updateId] = 0
                                await send('NO NEGATIVE YIKES ALLOWED\nYou cheeky monkey')
                                update = False
                            
                            if(update):
                                if(deltaYike > 0):
                                    await send('<@!' + updateId + '>.... <:yike:' + consts.YIKE_ID + '>\nYou now have ' + str(users[updateId]) + ' yikes')
                                else:
                                    await send('<@!' + updateId + '>, you have been forgiven\nYou now have ' + str(users[updateId]) + ' yikes')

                        else:
                            send('User not found')
                            print('ID not found: "' + updateId + '"')
                
                elif(re.fullmatch(consts.HELP_CMD, cmd)):
                    await send(consts.HELP_INFO)

                elif(re.fullmatch(consts.LIST_CMD, cmd)):
                    list = 'CURRENT YIKE TOTALS:\n'
                    for m in message.guild.members:
                        name = ''
                        if(str(m.nick) != "None"):
                            name = str(m.nick)
                        else:
                            name = str(m.name)

                        list += "\t" + name + ": " + str(users[str(m.id)]) + "\n"

                    await send(list)
                #Invalid Command
                else:
                    await send('Invalid Command: Try _help')

bot = Bot()
bot.run(token)
