# YikeSnake.py
import os
import re
import sys
import time
import json

import consts
import discord
import asyncio
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
users = {}


def getCurrentTime():
    curTime = time.localtime()
    timeList = [curTime.tm_year, curTime.tm_mon, curTime.tm_mday,
                curTime.tm_wday, curTime.tm_hour, curTime.tm_min]
    return timeList


def readDate(date):
    year = date[0]
    month = date[1]
    mday = date[2]

    if date[3] is 0:
        wday = "Mon"
    elif date[3] is 1:
        wday = "Tue"
    elif date[3] is 2:
        wday = "Wed"
    elif date[3] is 3:
        wday = "Thu"
    elif date[3] is 4:
        wday = "Fri"
    elif date[3] is 5:
        wday = "Sat"
    else:
        wday = "Sun"

    hour = date[4]
    minute = date[5]

    return f'( {wday} {month}/{mday}/{year % 1000} {hour}:{minute} )'


def writeQuote(subject, quote):
    try:
        with open(consts.QUOTES, mode="a") as f:
            out = ''
            for x in quote:
                out += x + " "

            curTime = getCurrentTime()
            f.write(json.dumps([subject, curTime, out]) + '\n')
    except OSError:
        print(time.asctime() + ": Error writing quote")


def getQuotes(userId):
    try:
        with open(consts.QUOTES, mode='r') as f:
            out = ''
            for line in f:
                quote = json.loads(line)
                if quote[0] == userId:
                    out += ' ' + readDate(quote[1]) + '\n' + quote[2] + '\n\n'

            return out
    except OSError:
        print(time.asctime() + ': Error reading quotes')


def getGuildQuotes(guild):
    try:
        with open(consts.QUOTES, mode='r') as f:
            out = ''
            for line in f:
                quote = json.loads(line)

                for m in guild.members:
                    if str(m.id) == quote[0]:
                        name = ''
                        if m.nick is not None:
                            name = m.nick
                        else:
                            name = m.name

                        out += name + ' ' + readDate(quote[1]) + '\n' + quote[2] + '\n\n'
                        break
            return out
    except OSError:
        print(time.asctime() + ': Error reading quotes')


def readFile():
    try:
        with open(consts.LOG) as f:
            for line in f:
                data = line.split(":")
                users.update({data[0]: int(data[1])})
    except OSError:
        print(time.asctime() + ": Error reading yike log")


def writeFile():
    try:
        with open(consts.LOG, 'w') as f:
            for userId in users:
                f.write(userId + ":" + str(users[userId]) + "\n")
    except OSError:
        print(time.asctime() + ": Error writing yike log")


def getId(rawId):
    if rawId[2] == '!':
        return rawId[3:-1]
    else:
        return rawId[2:-1]


def getName(guild, userId):
    name = ''
    for m in guild.members:
        if userId == str(m.id):
            if m.nick is not None:
                name = m.nick
            else:
                name = m.name
            break
    return name


async def sendUsage(send, cmd):
    if re.fullmatch(consts.YIKE_CMD, cmd):
        await send("Usage:\n" + consts.YIKE_USAGE)
    elif re.fullmatch(consts.UNYIKE_CMD, cmd):
        await send("Usage:\n" + consts.UNYIKE_USAGE)
    elif re.fullmatch(consts.QUOTE_CMD, cmd):
        await send("Usage:\n" + consts.QUOTE_USAGE)
    elif re.fullmatch(consts.GET_QUOTE_CMD, cmd):
        await send("Usage:\n" + consts.GET_QUOTE_USAGE)


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


async def voteUnyike(send: discord.TextChannel.send) -> bool:
    voter: discord.Message = await send(f'The legion shall decide your fate')

    await voter.add_reaction(consts.THUMBS_UP)
    await voter.add_reaction(consts.THUMBS_DOWN)

    await asyncio.sleep(10)

    cache_msg: discord.Message = discord.utils.get(bot.cached_messages, id=voter.id)

    up = 0
    down = 0
    for x in cache_msg.reactions:
        if x.emoji == consts.THUMBS_UP:
            up = x.count
        elif x.emoji == consts.THUMBS_DOWN:
            down = x.count
    return down + 1 >= up


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
                        updateId = getId(content[1])

                        if re.fullmatch(consts.YIKE_CMD, cmd):
                            deltaYike = 1
                        else:
                            deltaYike = -1
                            error = await voteUnyike(send)
                            if error:
                                await send("The yike shall stand")

                        # Check for optional amnt
                        if len(content) == 3:
                            if content[2].isnumeric():
                                amnt = int(content[2])
                                deltaYike *= amnt
                            else:
                                await sendUsage(send, cmd)
                                error = True

                        if updateId not in users:
                            error = True

                        name = getName(message.guild, updateId)

                        if not error:
                            update = await updateYike(send, updateId, deltaYike)

                            if update:
                                if deltaYike > 0:
                                    await send(name + '....<:yike:' + consts.YIKE_ID +
                                               '>\nYou now have ' + str(users[updateId]) + ' yikes')
                                else:
                                    await send(name + ', you have been forgiven\nYou now have ' + str(
                                        users[updateId]) + ' yikes')

                            else:
                                await send('User not found')
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

                # Write Quote
                elif re.fullmatch(consts.QUOTE_CMD, cmd):
                    err = False

                    if len(content) < 3:
                        err = True
                        await sendUsage(send, cmd)

                    if not err:
                        subject = getId(content[1])
                        writeQuote(subject, content[2:])
                        await send("Quote Recorded")
                # Get quotes
                elif re.fullmatch(consts.GET_QUOTE_CMD, cmd):
                    err = False
                    if len(content) > 2:
                        err = True
                        await sendUsage(send, cmd)

                    if not err:
                        dat = ''
                        if len(content) > 1 and re.fullmatch(consts.ID_FORMAT, content[1]):
                            dat = getQuotes(getId(content[1]))
                        else:
                            dat = getGuildQuotes(message.guild)

                        with open(consts.Q_OUTPUT, mode='w') as f:
                            f.write(dat)
                        with open(consts.Q_OUTPUT, mode='rb') as f:
                            await send(file=discord.File(f, filename='quotes.txt'))

                # Invalid Command
                else:
                    await send('Invalid Command: Try _help')


bot = YikeSnake()
bot.run(token)
