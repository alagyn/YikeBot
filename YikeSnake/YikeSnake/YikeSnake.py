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

            def sendUsage(send, cmd):
                if(re.fullmatch(consts.YIKE_CMD, cmd):
                    await send(consts.YIKE_USAGE)
                elif(re.fullmatch(consts.UNYIKE_CMD):
                    await send(consts.UNYIKE_USAGE)
                

            def updateYike(updateId, delta):
                users[updateId] += delta
                if(users[updateId] < 0):
                    users[updateId] = 0
                    await send('NO NEGATIVE YIKES ALLOWED\nYou cheeky monkey')
                    return False
                return True
                
            def getId(rawId):
                if(rawId[2] == '!'):
                    return rawId[3:-1]
                else:
                    return rawId[2:-1]

            if(len(content) > 0 and len(content[0]) > 0 and content[0][0] == '_'):
                
                cmd = content[0]
                
                #Update Yikes
                if(re.fullmatch(consts.YIKE_CMD, cmd) or re.fullmatch(consts.UNYIKE_CMD, cmd)):
                    
                    done = False

                    if(len(content) != 2 or len(content) != 3 or not re.fullmatch(consts.ID_FORMAT, content[1])):
                        sendUsage(send, cmd)
                        done = True
                    
                    if(not done):
                        deltaYike = 0
                        
                        if(re.fullmatch(consts.YIKE_CMD, cmd)):
                            deltaYike = 1
                        else:
                            deltaYike = -1
    
                        goof = False
                        if(len(content) == 3):
                            try:
                                deltaYike *= int(content[2)
                                
                            except ValueError:
                                sendUsage(send, cmd)
                                goof = True
                        
                        if(not goof):
                            updateId = getId(content[1)

                            if(updateId in users):
                                update = updateYike(updateId, deltaYike)
                                
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
                    if(len(content) == 1):
                        list = 'CURRENT YIKE TOTALS:\n'
                        for m in message.guild.members:
                            name = ''
                            if(str(m.nick) != "None"):
                                name = str(m.nick)
                            else:
                                name = str(m.name)

                            list += "\t" + name + ": " + str(users[str(m.id)]) + "\n"
                        await send(list)
                        
                    elif(len(content) == 2):
                        if(re.fullmatch(consts.ID_FORMAT, content[1])):
                            id = getId(content[1])
                            await send('<@!' + id + '> has ' + str(users[id]) + ' yikes'
                    else:
                        sendUsage(send, cmd)
                elif(re.fullmatch(consts.BIG_YIKE_CMD, cmd)):
                    
                #Invalid Command
                else:
                    await send('Invalid Command: Try _help')

bot = Bot()
bot.run(token)
