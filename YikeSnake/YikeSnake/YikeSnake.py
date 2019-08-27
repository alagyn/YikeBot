# YikeSnake.py
import os

import discord
import consts
import re
import sys

from dotenv import load_dotenv

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
users = {}

class YikeSnake(discord.Client):

    async def on_ready(self):
        print(f'{self.user} is logged in')
        for g in self.guilds:
            for m in g.members:
                users.update({str(m.id) : 0})
        YikeSnake.readFile()
        game = discord.Game("_help")
        await self.change_presence(status=discord.Status.online, activity=game)

    async def on_member_join(self, member):
        for g in self.guilds:
                for m in g.members:
                    if(str(m.id) not in users):
                        users.update({str(m.id) : 0})

    def readFile():
        with open(consts.LOG) as f:
            for line in f:
                data = line.split(":");
                users.update({data[0] : int(data[1])})

    def writeFile():
        with open(consts.LOG, 'w') as f:
            for id in users:
                f.write(id + ":" + str(users[id]) + "\n")
        
    async def on_message(self, message):
        if(message.author != self.user):
            content = message.content.split(' ')
            send = message.channel.send
            userFound = False

            #Funcs
            async def sendUsage(cmd):
                if(re.fullmatch(consts.YIKE_CMD, cmd)):
                    await send("Usage:\n" + consts.YIKE_USAGE)
                elif(re.fullmatch(consts.UNYIKE_CMD, cmd)):
                    await send("Usage:\n" + consts.UNYIKE_USAGE)
                
            async def updateYike(updateId, delta):
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

            #####

            if(len(content) > 0 and len(content[0]) > 0 and content[0][0] == '_'):
                
                cmd = content[0]
                
                #Update Yikes
                if(re.fullmatch(consts.YIKE_CMD, cmd) or re.fullmatch(consts.UNYIKE_CMD, cmd)):
                    
                    error = False

                    #Check command syntax
                    if((len(content) != 2 and len(content) != 3) or not re.fullmatch(consts.ID_FORMAT, content[1])):
                        await sendUsage(cmd)
                        error = True
                    
                    if(not error):
                        deltaYike = 0
                        
                        if(re.fullmatch(consts.YIKE_CMD, cmd)):
                            deltaYike = 1
                        else:
                            deltaYike = -1
                        
                        #Check for optional amnt
                        if(len(content) == 3):
                            if(content[2].isnumeric()):
                                amnt = int(content[2])
                                deltaYike *= amnt
                            else:
                                await sendUsage(cmd)
                                error = True
                        
                        if(not error):
                            updateId = getId(content[1])

                            if(updateId in users):
                                update = await updateYike(updateId, deltaYike)
                                
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
                
                #List current yikes
                elif(re.fullmatch(consts.LIST_CMD, cmd)):
                    #List all
                    if(len(content) == 1):
                        list = 'CURRENT YIKE TOTALS:\n'
                        for m in message.guild.members:
                            name = ''
                            #Check for Nickname
                            if(str(m.nick) != "None"):
                                name = str(m.nick)
                            else:
                                name = str(m.name)

                            list += "\t" + name + ": " + str(users[str(m.id)]) + "\n"
                        await send(list)
                    #list single                                            
                    elif(len(content) == 2):
                        if(re.fullmatch(consts.ID_FORMAT, content[1])):
                            id = getId(content[1])
                            await send('<@!' + id + '> has ' + str(users[id]) + ' yikes')
                        else:
                            await sendUsage(cmd)
                    else:
                        await sendUsage(cmd)
                #Ultra Admin logout
                elif(re.fullmatch(consts.LOGOUT_CMD, cmd)):
                    if(str(message.author.id) == consts.ADMIN_ID):
                        YikeSnake.writeFile()
                        print('YikeLog Updated, Logging out')
                        await self.change_presence(status=discord.Status.offline)
                        await discord.Client.close(self)

                #Invalid Command
                else:
                    await send('Invalid Command: Try _help')

bot = YikeSnake()
bot.run(token)
