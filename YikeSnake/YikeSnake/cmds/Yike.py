# Yike.py
import re
import discord

from consts import YIKE_CMD
from consts import YIKE_ID
from consts import THUMBS_DOWN
from consts import THUMBS_UP
from utils.userUtil import *
from asyncio import sleep


async def yikeCmd(bot, send, message: discord.Message, content):
    cmd = content[0]
    error = False
    users = bot.users

    updateId = getId(content[1])

    if re.fullmatch(YIKE_CMD, cmd):
        deltaYike = 1
    else:
        deltaYike = -1
        error = await voteUnyike(bot, send)
        if error:
            await send("The yike shall stand")

    if not error:
        # Check for optional amnt
        if len(content) == 3:
            if content[2].isnumeric():
                amnt = int(content[2])
                deltaYike *= amnt
            else:
                await bot.sendUsage(send, cmd)
                error = True

        if updateId not in users:
            error = True

        name = getName(message.guild, updateId)

        if not error:
            update = await updateYike(send, users, updateId, deltaYike)

            if update:
                if deltaYike > 0:
                    await send(name + '....<:yike:' + YIKE_ID +
                               '>\nYou now have ' + str(users[updateId]) + ' yikes')
                else:
                    await send(name + ', you have been forgiven\nYou now have ' + str(
                        users[updateId]) + ' yikes')

            else:
                await send('User not found')
                print('ID not found: "' + updateId + '"')


async def updateYike(send, users, updateId, delta):
    users[updateId] += delta
    if users[updateId] < 0:
        users[updateId] = 0
        await send('NO NEGATIVE YIKES ALLOWED\nYou cheeky monkey')
        return False
    return True


async def voteUnyike(cur: discord.Client, send: discord.TextChannel.send) -> bool:
    voter: discord.Message = await send('The legion shall decide your fate')

    await voter.add_reaction(THUMBS_UP)
    await voter.add_reaction(THUMBS_DOWN)

    await sleep(10)

    cache_msg: discord.Message = discord.utils.get(cur.cached_messages, id=voter.id)

    up = 0
    down = 0
    for x in cache_msg.reactions:
        if x.emoji == THUMBS_UP:
            up = x.count
        elif x.emoji == THUMBS_DOWN:
            down = x.count
    # return down + 1 >= up
    return down >= up
