# quote.py

from discord.ext import commands
import discord
import json
import typing

from utils.timeUtils import *
import yikeSnake

from consts import QUOTE_LOG, REPLY_DELETE_TIME, Q_OUTPUT, THUMBS_UP

Q_ID_IDX = 0
Q_DATE_IDX = 1
Q_CONTENT_IDX = 2

MESSAGE_OUTPUT_FLAG = '-m'
MAX_MESSAGE_LEN = 1000


class Quote(commands.Cog):

    def __init__(self, bot: yikeSnake.YikeSnake):
        # References to the messages sent
        self.currentMessages = []
        # Reference to the bot
        self.bot = bot
        # IDK
        self._last_member = None

    async def cog_before_invoke(self, ctx):
        # Reset the current msgs to just the new context
        self.currentMessages = []

    async def cog_after_invoke(self, ctx):
        # Sets the previous set msgs in the bot
        self.bot.setPreviousMsgs(self.currentMessages, ctx)

    @commands.command(name="edit", rest_is_raw=True, brief='_edit <delta> <new message>', usage='<delta> <message>',
                      help='Edits a quote, where delta is the number of previous quotes, with 0 being the '
                           'most recent quote')
    async def edit(self, ctx: commands.Context, delta: int, *, arg: str):
        if delta < 0:
            self.currentMessages = [await ctx.send_help(ctx.command)]
            return

        lines = []
        try:
            with open(QUOTE_LOG, mode='r') as f:
                for x in f:
                    lines.append(x)
        except FileNotFoundError:
            self.currentMessages = [await ctx.send('No quotes to edit')]
            return

        toEdit = len(lines) - 1 - delta

        if toEdit < 0:
            self.currentMessages = [await ctx.send_help(ctx.command)]
            return

        x = json.loads(lines[toEdit])
        x[Q_CONTENT_IDX] = arg
        lines[toEdit] = json.dumps(x) + '\n'

        with open(QUOTE_LOG, mode='w') as f:
            for line in lines:
                f.write(line)

        await ctx.message.add_reaction(THUMBS_UP)

    @commands.command(name="quote", rest_is_raw=True, brief="_quote <user> <message>", usage="<user> <message>",
                      help="Adds a quote for a user to a running log")
    async def quote(self, ctx: commands.Context, *, arg: str):
        # Retrieve a new UserConverter
        converter = commands.UserConverter()
        # Strip leading/trailing spaces
        arg = arg.strip()
        try:
            # Split the args by spaces
            content = arg.split(' ')
            # Check if there is less than 2 args
            if len(content) < 2:
                self.currentMessages = [await ctx.send_help()]
                return

            # try to convert the first argument into a user
            user: discord.User = await converter.convert(ctx=ctx, argument=content[0])
        except commands.CommandError:
            self.currentMessages = [await ctx.send("Invalid user")]
            return

        # Finds the end of the quote author's @
        qMessage = arg[arg.find('>') + 1:]
        qMessage = qMessage.strip()

        # Set JSON output
        jOuput = [user.id, getCurrentTime(), qMessage]

        # Write the JSON to file
        try:
            with open(QUOTE_LOG, mode='a') as f:
                f.write(f'{json.dumps(jOuput)}\n')
        except OSError:
            self.bot.addAdminLog(f"Error writing quote, author: {ctx.author.name}, channel: {ctx.channel.name}:"
                                 f" {ctx.message.content}")

        await ctx.message.add_reaction(THUMBS_UP)
        # await ctx.send('Quote recorded', delete_after=REPLY_DELETE_TIME)

    @commands.command(name="getQuotes", aliases=["getQuote"], help='Returns all the quotes for a server or user, '
                                                                   '-m flag for message output',
                      brief='_[getQuotes|getQuote] [user] [-m]')
    async def getQuotes(self, ctx: commands.Context, user: typing.Optional[discord.User] = None,
                        mode: typing.Optional[str] = None):

        fileName = ''
        output = []

        if user is not None:
            # set up filename for single user quotes
            temp = user.display_name.split(' ')
            for x in temp:
                fileName += f'{x}_'

            # Retrieve quotes with single user id
            try:
                with open(QUOTE_LOG, mode='r') as f:
                    for line in f:
                        curQuote = json.loads(line)
                        if str(user.id).__eq__(str(curQuote[Q_ID_IDX])):
                            output.append(f'{readDate(curQuote[Q_DATE_IDX])}\n'
                                          f'{curQuote[Q_CONTENT_IDX]}')
            except FileNotFoundError:
                return

        else:
            # Retrieve quotes for server
            try:
                with open(QUOTE_LOG, mode='r') as f:
                    for line in f:
                        curQuote = json.loads(line)
                        curUser = discord.utils.get(ctx.guild.members, id=int(curQuote[Q_ID_IDX]))
                        if curUser is not None:
                            output.append(f'{curUser.display_name} {readDate(curQuote[Q_DATE_IDX])}\n'
                                          f'{curQuote[Q_CONTENT_IDX]}')
            except FileNotFoundError:
                return
        fileName += 'quotes.txt'

        if len(output).__eq__(0):
            await ctx.send("No quotes found", delete_after=REPLY_DELETE_TIME)
            return

        # Check for message mode flag
        # Splits msg to not exceed MAX_MESSAGE_LEN
        if mode is not None and mode.__eq__(MESSAGE_OUTPUT_FLAG):
            count = 0
            curMessage = ''
            for x in output:
                if count + len(x) >= MAX_MESSAGE_LEN:
                    count = 0
                    self.currentMessages.append(await ctx.send(curMessage))
                    curMessage = ''
                else:
                    curMessage += f'{x}\n\n'
                    count += len(x)

            if count > 0:
                self.currentMessages.append(await ctx.send(curMessage))
        else:
            # Write to output file and send as attachment
            with open(Q_OUTPUT, mode='w') as f:
                for x in output:
                    f.write(f'{x}\n\n')
            with open(Q_OUTPUT, mode='rb') as f:
                self.currentMessages = [await ctx.send(file=discord.File(f, filename=fileName))]

    # Error handling
    async def cog_command_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.BadArgument):
            self.currentMessages = [await ctx.send_help(ctx.command)]
        else:
            raise error


def setup(bot):
    bot.add_cog(Quote(bot))
