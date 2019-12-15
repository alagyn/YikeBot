# quote.py

from discord.ext import commands
import discord
import json
import typing

from utils.timeUtils import *
import yikeSnake

from consts import QUOTE_LOG, REPLY_DELETE_TIME, Q_OUTPUT

Q_ID_IDX = 0
Q_DATE_IDX = 1
Q_CONTENT_IDX = 2

MESSAGE_OUTPUT_FLAG = '-m'
MAX_MESSAGE_LEN = 1000


class Quote(commands.Cog):

    def __init__(self, bot: yikeSnake.YikeSnake):
        self.message = [discord.Message]
        self.bot = bot
        self._last_member = None

    async def cog_before_invoke(self, ctx):
        self.message = []

    async def cog_after_invoke(self, ctx):
        self.bot.lastMessage = []
        for x in self.message:
            self.bot.lastMessage.append(x.id)
        self.bot.lastCmd = ctx.message.id

    @commands.command(name="quote", rest_is_raw=True, brief="_quote <user> <message>", usage="<user> <message>",
                      help="Adds a quote for a user to a running log")
    async def quote(self, ctx: commands.Context, *, arg: str):
        x = commands.UserConverter()
        arg = arg.strip()
        try:
            content = arg.split(' ')
            if len(content) < 2:
                self.message = [await ctx.send_help()]
                return

            user: discord.User = await x.convert(ctx=ctx, argument=content[0])
        except commands.CommandError:
            self.message = [await ctx.send("Invalid user")]
            return

        qMessage = arg[arg.find('>') + 1:]
        qMessage = qMessage.strip()

        jOuput = [user.id, getCurrentTime(), qMessage]

        try:
            with open(QUOTE_LOG, mode='a') as f:
                f.write(f'{json.dumps(jOuput)}\n')
        except OSError:
            self.bot.addAdminLog(f"Error writing quote, author: {ctx.author.name}, channel: {ctx.channel.name}:"
                                 f" {ctx.message.content}")

        await ctx.send('Quote recorded', delete_after=REPLY_DELETE_TIME)

    @commands.command(name="getQuotes", aliases=["getQuote"], help='Returns all the quotes for a server or user, '
                                                                   '-m flag for message output',
                      brief='_[getQuotes|getQuote] [user] [-m]')
    async def getQuotes(self, ctx: commands.Context, user: typing.Optional[discord.User] = None,
                        mode: typing.Optional[str] = None):
        fileName = ''
        output = []

        if user is not None:
            temp = user.display_name.split(' ')
            for x in temp:
                fileName += f'{x}_'

            with open(QUOTE_LOG, mode='r') as f:
                for line in f:
                    curQuote = json.loads(line)
                    if str(user.id).__eq__(str(curQuote[Q_ID_IDX])):
                        output.append(f'{readDate(curQuote[Q_DATE_IDX])}\n'
                                      f'{curQuote[Q_CONTENT_IDX]}')

        else:
            with open(QUOTE_LOG, mode='r') as f:
                for line in f:
                    curQuote = json.loads(line)
                    curUser = discord.utils.get(ctx.guild.members, id=int(curQuote[Q_ID_IDX]))
                    if curUser is not None:
                        output.append(f'{curUser.display_name} {readDate(curQuote[Q_DATE_IDX])}\n'
                                      f'{curQuote[Q_CONTENT_IDX]}')

        fileName += 'quotes.txt'

        if len(output).__eq__(0):
            await ctx.send("No quotes found", delete_after=REPLY_DELETE_TIME)
            return

        if mode is not None and mode.__eq__(MESSAGE_OUTPUT_FLAG):
            count = 0
            curMessage = ''
            for x in output:
                if count + len(x) >= MAX_MESSAGE_LEN:
                    count = 0
                    self.message.append(await ctx.send(curMessage))
                    curMessage = ''
                else:
                    curMessage += f'{x}\n\n'
                    count += len(x)

            if count > 0:
                self.message.append(await ctx.send(curMessage))
        else:
            with open(Q_OUTPUT, mode='w') as f:
                for x in output:
                    f.write(f'{x}\n\n')
            with open(Q_OUTPUT, mode='rb') as f:
                self.message = [await ctx.send(file=discord.File(f, filename=fileName))]

    async def cog_command_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.BadArgument):
            self.message = [await ctx.send_help(ctx.command)]
        else:
            raise error


def setup(bot):
    bot.add_cog(Quote(bot))
