# yike.py
from discord.ext import commands
import typing
import discord
from asyncio import sleep
import json

from consts import YIKE_EMOJI_ID
from consts import THUMBS_UP
from consts import THUMBS_DOWN
from consts import YIKE_LOG

import yikeSnake


class Yike(commands.Cog):
    AUDIENCE_ERROR = "Thou shalt not use yike commands in " \
                     "channels not visible to at least half the server"
    YIKE_DESC = "Adds one or more Yikes to a user"
    YIKE_USAGE = '<user> [amount]'
    UNYIKE_USAGE = "Removes one or more Yikes from a user"
    LIST_DESC = 'Lists the yikes for every user or a single user'

    def __init__(self, bot: yikeSnake.YikeSnake):
        self.bot: yikeSnake.YikeSnake = bot
        self._last_member = None
        self.message = [discord.Message]
        self.yikeLog = {}

    async def cog_before_invoke(self, ctx):
        self.message = []
        if len(self.yikeLog) == 0:
            self.readYikeLog()

    async def cog_after_invoke(self, ctx):
        self.bot.setPreviousMsgs(self.message, ctx)
        if len(self.yikeLog) > 0:
            self.writeYikeLog()

    # Error handling
    async def cog_command_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.BadArgument):
            self.message = [await ctx.send_help(ctx.command)]
        else:
            raise error

    @commands.Cog.listener(name='on_member_join')
    async def on_member_join(self, member: discord.Member):
        print("Member joined")
        self.yikeLog.update({member.id: 0})

    @commands.Cog.listener(name='on_ready')
    async def on_ready(self):
        for g in self.bot.guilds:
            for m in g.members:
                self.yikeLog[m.id] = 0
        self.readYikeLog()

    # YIKE
    @commands.command(name="yike", help=YIKE_DESC, aliases=['y'],
                      brief='_yike <user> [amount]', usage='<user> [amount]')
    async def yike(self, ctx, user: discord.Member, amnt=1):
        if await self.checkChannel(ctx):
            return

        if amnt <= 0:
            self.message = [await ctx.send("Invalid amount")]
            return

        self.yikeLog[user.id] += amnt
        self.bot.addAdminLog(f'Yike of {user} initiated by {ctx.author} '
                             f'in channel {ctx.channel.name} : {ctx.message.content}')
        self.message = [await ctx.send(f'{user.display_name}... <:yike:{YIKE_EMOJI_ID}>\n'
                                       f'You now have {self.yikeLog[user.id]} yikes')]

    # UNYIKE
    @commands.command(name="unyike", help=UNYIKE_USAGE, aliases=['uy'],
                      brief='_unyike <user> [amount]', usage='<user> [amount]')
    async def unYike(self, ctx, user: discord.Member, amnt=1):
        if await self.checkChannel(ctx):
            return

        if self.yikeLog[user.id] == 0:
            self.message = [await ctx.send("NO NEGATIVE YIKES\nYou cheeky monkey")]
            return

        voter: discord.Message = await ctx.send("The legion shall decide your fate")

        await voter.add_reaction(THUMBS_UP)
        await voter.add_reaction(THUMBS_DOWN)

        await sleep(self.bot.waitTime)

        cacheMsg: discord.Message = discord.utils.get(self.bot.cached_messages, id=voter.id)
        up = 0
        down = 0
        upVoters = ''
        downVoters = ''

        for x in cacheMsg.reactions:
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

        self.bot.addAdminLog(f'Unyike of {user} initiated by {ctx.author} in channel "{ctx.channel.name}"'
                             f' : {ctx.message.content}\n'
                             f'\tUpVotes: {upVoters}\n\tDownVotes: {downVoters}')
        await cacheMsg.delete()

        if down + 1 >= up:
            self.message = [await ctx.send("The yike shall stand")]
        else:
            self.yikeLog[user.id] -= amnt
            self.message = [await ctx.send(f"{user.display_name}, you have been forgiven\n"
                                           f"you now have {str(self.yikeLog[user.id])}")]

    # Channel check
    async def checkChannel(self, ctx) -> bool:
        x = len(ctx.channel.members) < len(ctx.guild.members) / 2
        if x:
            self.bot.addAdminLog(f'Yike/Unyike audience too small, initiated by {ctx.author.name} '
                                 f'in channel {ctx.channel.name} : "{ctx.message.content}"')
            self.message = [await ctx.send(self.AUDIENCE_ERROR)]
        return x

    # LIST
    @commands.command(name="list", help=LIST_DESC, brief='_list [user]', usage='[user]')
    async def list(self, ctx, user: typing.Optional[discord.User] = None):
        output = ''

        if user is None:
            for m in ctx.guild.members:
                output += f'{m.display_name}: {self.yikeLog[m.id]}\n'
        else:
            output = f'{user.display_name} has {self.yikeLog[user.id]}'

        self.message = [await ctx.send(output)]

    def writeYikeLog(self):
        with open(YIKE_LOG, mode='w') as f:
            for userId in self.yikeLog:
                f.write(f'{json.dumps([userId, self.yikeLog[userId]])}\n')

    def readYikeLog(self):
        with open(YIKE_LOG, mode='r') as f:
            i = 1
            for line in f:
                try:
                    x = json.loads(line)
                    self.yikeLog[int(x[0])] = x[1]
                except KeyError as e:
                    print(f'KeyError yikelog line {i}: "{line}"\n'
                          f'\t{e}')
                except json.JSONDecodeError as e:
                    print(f'Decode error line {i}: "{line}"\n'
                          f'\t{e}')
                i += 1


def setup(bot):
    bot.add_cog(Yike(bot))