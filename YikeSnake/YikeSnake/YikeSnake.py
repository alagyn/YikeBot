# YikeSnake.py
import os
import re
import sys
import time

import consts
import discord
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
users = {}


def writeQuote(param):
    pass


def readFile():
    try:
        with open(consts.LOG) as f:
            for line in f:
                data = line.split(":")
                users.update({data[0]: int(data[1])})
    except OSError:
        pass


def writeFile():
    try:
        with open(consts.LOG, 'w') as f:
            for id in users:
                f.write(id + ":" + str(users[id]) + "\n")
    except OSError:
        pass


async def sendUsage(send, cmd):
    if re.fullmatch(consts.YIKE_CMD, cmd):
        await send("Usage:\n" + consts.YIKE_USAGE)
    elif re.fullmatch(consts.UNYIKE_CMD, cmd):
        await send("Usage:\n" + consts.UNYIKE_USAGE)


async def updateYike(send, updateId, delta):
    users[updateId] += delta
    if users[updateId] < 0:
        users[updateId] = 0
        await send('NO NEGATIVE YIKES ALLOWED\nYou cheeky monkey')
        return False
    return True


async def on_member_join(member):
    if str(member.id) not in users:
        users.update({str(member.id): 0})


class YikeSnake(discord.Client):

    async def on_ready(self):
        print(time.asctime() + ": " + f'{self.user} is logged in')
        for g in self.guilds:
            for m in g.members:
                users.update({str(m.id): 0})
        readFile()
        game = discord.Game("_help")
        await self.change_presence(status=discord.Status.online, activity=game)

    async def on_message(self, message):
        if message.author != self.user:
            content = message.content.split(' ')
            send = message.channel.send

            # Funcs -------

            def getId(rawId):
                if rawId[2] == '!':
                    return rawId[3:-1]
                else:
                    return rawId[2:-1]

            # -----------

            if len(content) > 0 and len(content[0]) > 0 and content[0][0] == '_':

                cmd = content[0]

                # Update Yikes
                if re.fullmatch(consts.YIKE_CMD, cmd) or re.fullmatch(consts.UNYIKE_CMD, cmd):

                    error = False

                    # Check command syntax
                    if (len(content) != 2 and len(content) != 3) or not re.fullmatch(consts.ID_FORMAT, content[1]):
                        await sendUsage(send, cmd)
                        error = True

                    if not error:
                        if re.fullmatch(consts.YIKE_CMD, cmd):
                            deltaYike = 1
                        else:
                            deltaYike = -1

                        # Check for optional amnt
                        if len(content) == 3:
                            if content[2].isnumeric():
                                amnt = int(content[2])
                                deltaYike *= amnt
                            else:
                                await sendUsage(send, cmd)
                                error = True

                        if not error:
                            updateId = getId(content[1])

                            if updateId in users:
                                update = await updateYike(send, updateId, deltaYike)

                                if update:
                                    if deltaYike > 0:
                                        await send('<@!' + updateId + '>.... <:yike:' + consts.YIKE_ID +
                                                   '>\nYou now have ' + str(users[updateId]) + ' yikes')
                                    else:
                                        await send('<@!' + updateId + '>, you have been forgiven\nYou now have ' + str(
                                            users[updateId]) + ' yikes')

                            else:
                                send('User not found')
                                print('ID not found: "' + updateId + '"')

                elif re.fullmatch(consts.HELP_CMD, cmd):
                    await send(consts.HELP_INFO)

                # List current yikes
                elif re.fullmatch(consts.LIST_CMD, cmd):
                    # List all
                    if len(content) == 1:
                        nameList = 'CURRENT YIKE TOTALS:\n'
                        for m in message.guild.members:
                            # Check for Nickname
                            if str(m.nick) != "None":
                                name = str(m.nick)
                            else:
                                name = str(m.name)

                            nameList += "\t" + name + ": " + str(users[str(m.id)]) + "\n"
                        await send(nameList)
                    # list single
                    elif len(content) == 2:
                        if re.fullmatch(consts.ID_FORMAT, content[1]):
                            userId = getId(content[1])
                            await send('<@!' + userId + '> has ' + str(users[userId]) + ' yikes')
                        else:
                            await sendUsage(send, cmd)
                    else:
                        await sendUsage(send, cmd)
                # Ultra Admin logout
                elif re.fullmatch(consts.LOGOUT_CMD, cmd):
                    if str(message.author.id) == consts.ADMIN_ID:
                        writeFile()
                        print(time.asctime() + ': YikeLog Updated, Logging out')
                        await self.change_presence(status=discord.Status.offline)
                        await discord.Client.close(self)
                        sys.exit(0)

                elif re.fullmatch(consts.QUOTE_CMD, cmd):
                    err = False

                    if len(content) < 4:
                        err = True
                        await sendUsage(send, cmd)

                    if content[2] != "-":
                        err = True
                        await sendUsage(send, cmd)

                    if not err:
                        writeQuote(content[3:])

                # Invalid Command
                else:
                    await send('Invalid Command: Try _help')


bot = YikeSnake()
bot.run(token)
