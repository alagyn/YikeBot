# Yike.py
import re
import discord

from consts import YIKE_CMD
from consts import YIKE_ID
from consts import THUMBS_DOWN
from consts import THUMBS_UP
from utils.userUtil import *
from asyncio import sleep
from utils.timeUtils import *


async def yikeCmd(bot, send, message: discord.Message, content):
    cmd = content[0]
    error = False
    users = bot.users

    updateId = getId(content[1])

    if updateId not in users:
        bot.addOutputLog(f'ID not found: "{updateId}"')
        await send('User not found')
        return

    fullName = getFullName(message.guild, updateId)
    name = getName(message.guild, updateId)

    if checkChannel(message.channel):
        bot.addOutputLog(f'Yike/Unyike audience too small, initiated by {message.author.name} in '
                         f'{message.channel.name}. Message: "{message.content}"')
        await send('Thou shalt not Yike in channels not visible to at least half the server')
        return

    deltaYike = 0
    if re.fullmatch(YIKE_CMD, cmd):
        deltaYike = 1
    else:
        deltaYike = -1
        if await voteUnyike(bot, send, fullName, message.author.name):
            await send("The yike shall stand")
            return

    # Check for optional amnt
    if len(content) == 3:
        if content[2].isnumeric():
            amnt = int(content[2])
            deltaYike *= amnt
        else:
            await bot.sendUsage(send, cmd)
            return

    update = await updateYike(send, users, updateId, deltaYike)

    if update:
        if deltaYike > 0:
            await send(name + '....<:yike:' + YIKE_ID +
                       f'>\nYou now have {str(users[updateId])} yikes')
            bot.addOutputLog(f'Yike of "{fullName}" initiated by "{message.author.name}"')
        else:
            await send(name + ', you have been forgiven\nYou now have ' + str(
                users[updateId]) + ' yikes')


async def updateYike(send, users, updateId, delta):
    users[updateId] += delta
    if users[updateId] < 0:
        users[updateId] = 0
        await send('NO NEGATIVE YIKES ALLOWED\nYou cheeky monkey')
        return False
    return True


def checkChannel(channel) -> bool:
    return len(channel.members) < len(channel.guild.members) / 2


async def voteUnyike(cur, send: discord.TextChannel.send, name: str, initiator: str) -> bool:
    voter: discord.Message = await send('The legion shall decide your fate')

    await voter.add_reaction(THUMBS_UP)
    await voter.add_reaction(THUMBS_DOWN)

    await sleep(cur.waitTime)

    cache_msg: discord.Message = discord.utils.get(cur.cached_messages, id=voter.id)
    up = 0
    down = 0
    upVoters = ""
    downVoters = ""
    for x in cache_msg.reactions:
        if x.emoji == THUMBS_UP:
            up = x.count
            users = await x.users().flatten()
            for u in users:
                upVoters += u.name + '  '
        elif x.emoji == THUMBS_DOWN:
            down = x.count
            users = await x.users().flatten()
            for u in users:
                downVoters += u.name + '  '

    cur.addOutputLog(f'Unyike of {name} initiated by {initiator}')
    cur.addOutputLog(f'\tUpVotes: {upVoters}\n\tDownVotes: {downVoters}')
    return down + 1 >= up
