# yike.py
from discord.ext import commands
import typing
import discord
from asyncio import sleep

from consts import YIKE_EMOJI_ID
from consts import THUMBS_UP
from consts import THUMBS_DOWN

AUDIENCE_ERROR = "Thou shalt not use yike commands in " \
                 "channels not visible to at least half the server"

YIKE_DESC = "Adds one or more Yikes to a user"
YIKE_USAGE = '<user> [amount]'
UNYIKE_USAGE = "Removes one or more Yikes from a user"
LIST_DESC = 'Lists the yikes for every user or a single user'


class Yike(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None
        self.message = [discord.Message]

    async def cog_before_invoke(self, ctx):
        self.message = []

    async def cog_after_invoke(self, ctx):
        self.bot.lastMessage = []
        for x in self.message:
            self.bot.lastMessage.append(x.id)
        self.bot.lastCmd = ctx.message.id

        await self.bot.writeYikeLog()

    # YIKE
    @commands.command(name="yike", help=YIKE_DESC, brief='_yike <user> [amount]', usage='<user> [amount]')
    async def yike(self, ctx, user: discord.Member, amnt=1):
        if await self.checkChannel(ctx):
            return

        if amnt <= 0:
            self.message = [await ctx.send("Invalid amount")]
            return

        self.bot.users[str(user.id)] += amnt
        self.bot.addAdminLog(f'Yike of {user.name} initiated by {ctx.author.name} '
                             f'in channel {ctx.channel.name} : {ctx.message.content}')
        self.message = [await ctx.send(f'{user.display_name}... <:yike:{YIKE_EMOJI_ID}>\n'
                                       f'You now have {self.bot.users[str(user.id)]} yikes')]

    # UNYIKE
    @commands.command(name="unyike", help=UNYIKE_USAGE, brief='_unyike <user> [amount]', usage='<user> [amount]')
    async def unYike(self, ctx, user: discord.Member, amnt=1):
        if await self.checkChannel(ctx):
            return

        if self.bot.users[str(user.id)] == 0:
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

        self.bot.addAdminLog(f'Unyike of {user.display_name} initiated by {ctx.author} in channel {ctx.channel.name}'
                             f' : {ctx.message.content}\n'
                             f'\tUpVotes: {upVoters}\n\tDownVotes: {downVoters}')
        await cacheMsg.delete()

        if down + 1 >= up:
            self.message = [await ctx.send("The yike shall stand")]
        else:
            self.bot.users[str(user.id)] -= amnt
            self.message = [await ctx.send(f"{user.display_name}, you have been forgiven\n"
                                           f"you now have {str(self.bot.users[user.id])}")]

    # Channel check
    async def checkChannel(self, ctx) -> bool:
        x = len(ctx.channel.members) < len(ctx.guild.members) / 2
        if x:
            self.bot.addAdminLog(f'Yike/Unyike audience too small, initiated by {ctx.author.name} '
                                 f'in channel {ctx.channel.name} : "{ctx.message.content}"')
            self.message = [await ctx.send(AUDIENCE_ERROR)]
        return x

    # LIST
    @commands.command(name="list", help=LIST_DESC, brief='_list [user]', usage='[user]')
    async def list(self, ctx, user: typing.Optional[discord.User] = None):
        output = ''

        if user is None:
            for m in ctx.guild.members:
                output += f'{m.display_name}: {self.bot.users[str(m.id)]}\n'
        else:
            output = f'{user.display_name} has {self.bot.users[str(user.id)]}'

        self.message = [await ctx.send(output)]

    # Error handling
    async def cog_command_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send_help()
        else:
            await ctx.send(error)


def setup(bot):
    bot.add_cog(Yike(bot))
