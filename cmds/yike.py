# yike.py
from discord.ext import commands
from discord.ext import tasks
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
        self.previousMsgs = [discord.Message]
        self.yikeLog = {}

        self.backupYikeLog.change_interval(minutes=bot.backupTime)
        self.backupYikeLog.start()

    def cog_unload(self):
        # TODO handle mid backup cancels?
        # self.backupYikeLog.cancel()
        pass

    async def cog_before_invoke(self, ctx):
        self.previousMsgs = []
        if len(self.yikeLog) == 0:
            self.readYikeLog()

    async def cog_after_invoke(self, ctx):
        self.bot.setPreviousMsgs(self.previousMsgs, ctx)
        if len(self.yikeLog) > 0:
            self.writeYikeLog(YIKE_LOG)

    # Error handling
    async def cog_command_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.UserInputError):
            self.previousMsgs = [await ctx.send_help(ctx.command)]

    @commands.Cog.listener(name='on_member_join')
    async def on_member_join(self, member: discord.Member):
        self.bot.addAdminLog(f"Member joined {member.nick}")
        self.yikeLog.update({member.id: 0})

    @commands.Cog.listener(name='on_ready')
    async def on_ready(self):
        # Init yikeLog
        for g in self.bot.guilds:
            for m in g.members:
                self.yikeLog[m.id] = 0
        self.readYikeLog()


    @tasks.loop()
    async def backupYikeLog(self):
        if not self.bot.is_closed():
            self.writeYikeLog(self.bot.backupFolder + 'yike_backup.dat')
            self.bot.addAdminLog('Yike Log backup complete')

    @backupYikeLog.before_loop
    async def beforeBackup(self):
        await self.bot.wait_until_ready()
        self.bot.addAdminLog("Yike Log backup init")

    @backupYikeLog.after_loop
    async def onBackupCancel(self):
        if self.backupYikeLog.is_being_cancelled():
            self.bot.addAdminLog("Yike Log backup shutdown")

    # YIKE
    @commands.command(name="yike", help=YIKE_DESC, aliases=['y'],
                      brief='_yike <user> [amount]', usage='<user> [amount]')
    async def yike(self, ctx, user: discord.Member, amnt=1):
        # Check the channel for correct users
        if await self.checkChannel(ctx):
            return

        if amnt <= 0:
            self.previousMsgs = [await ctx.send("Invalid amount")]
            return

        self.yikeLog[user.id] += amnt
        self.bot.addAdminLog(f'Yike of {user} initiated by {ctx.author} '
                             f'in channel {ctx.channel.name} : {ctx.message.content}')

        self.previousMsgs = [await ctx.send(f'{user.display_name}... <:yike:{YIKE_EMOJI_ID}>\n'
                                            f'You now have {self.yikeLog[user.id]} yikes')]

    # UNYIKE
    @commands.command(name="unyike", help=UNYIKE_USAGE, aliases=['uy'],
                      brief='_unyike <user> [amount]', usage='<user> [amount]')
    async def unYike(self, ctx, user: discord.Member, amnt=1):
        if await self.checkChannel(ctx):
            return

        # Check for zero yikes
        if self.yikeLog[user.id] == 0:
            self.previousMsgs = [await ctx.send("NO NEGATIVE YIKES\nYou cheeky monkey")]
            return

        # Send voter yikes
        voter: discord.Message = await ctx.send("The legion shall decide your fate")

        await voter.add_reaction(THUMBS_UP)
        await voter.add_reaction(THUMBS_DOWN)

        await sleep(self.bot.waitTime)

        cacheMsg: discord.Message = discord.utils.get(self.bot.cached_messages, id=voter.id)
        up = 0
        down = 0
        upVoters = ''
        downVoters = ''

        # Count reactions
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

        # Unyike if upvotes are at least 2 greater
        if down + 1 >= up:
            self.previousMsgs = [await ctx.send("The yike shall stand")]
        else:
            self.yikeLog[user.id] -= amnt
            self.previousMsgs = [await ctx.send(f"{user.display_name}, you have been forgiven\n"
                                                f"you now have {str(self.yikeLog[user.id])}")]

    # Channel check
    async def checkChannel(self, ctx) -> bool:
        # Make sure that channel has at least half of the server members
        x = len(ctx.channel.members) < len(ctx.guild.members) / 2
        if x:
            self.bot.addAdminLog(f'Yike/Unyike audience too small, initiated by {ctx.author.name} '
                                 f'in channel {ctx.channel.name} : "{ctx.message.content}"')
            self.previousMsgs = [await ctx.send(self.AUDIENCE_ERROR)]
        return x

    # LIST
    @commands.command(name="list", help=LIST_DESC, brief='_list [user]', usage='[user]')
    async def list(self, ctx, user: typing.Optional[discord.Member] = None):
        output = ''

        class TempItem:
            def __init__(self, name: str, _amnt: int):
                self.name = name
                self.amnt = _amnt

            def __gt__(self, other):
                if self.amnt > other.amnt:
                    return False

                if self.amnt < other.amnt:
                    return True

                return self.name > other.name

            def __lt__(self, other):
                if self.amnt < other.amnt:
                    return False

                if self.amnt > other.amnt:
                    return True

                return self.name < other.name


        temp = []
        if user is None:
            for m in ctx.guild.members:
                amnt = self.yikeLog[m.id]
                if amnt > 0:
                    temp.append(TempItem(m.display_name, amnt))

            temp.sort()
            for m in temp:
                output += f'{m.name}: {m.amnt}\n'
        else:
            output = f'{user.display_name} has {self.yikeLog[user.id]}'

        self.previousMsgs = [await ctx.send(output)]

    def writeYikeLog(self, file):
        with open(file, mode='w') as f:
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
