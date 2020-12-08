# music.py
from discord.ext import commands
from discord.ext.commands import Context
import discord
import asyncio
import typing

from yikeSnake import YikeSnake

from consts import PAUSE_ICON, PLAY_ICON, THUMBS_UP


def setup(bot):
    bot.add_cog(Music(bot))


class Music(commands.Cog):
    def __init__(self, bot: YikeSnake):
        self.bot = bot

    MUSIC_HELP = 'Commands to play music in a voice channel, calling with no sub command activates the play command'
    MUSIC_BRIEF = 'Commands to play music'

    @commands.group(name='music', aliases=['m'], invoke_without_command=True, help=MUSIC_HELP, brief=MUSIC_BRIEF)
    async def music(self, ctx: Context, *, args=''):
        await self.play(ctx, query=args)

    JOIN_HELP = 'Connects the bot to your current voice channel'

    @music.command(name='join', aliases=['j', 'connect', 'c'], help=JOIN_HELP)
    async def join(self, ctx: Context):
        # TODO join
        pass

    LEAVE_HELP = 'Disconnects the bot and stops playback. Clears the playback queue'
    LEAVE_BRIEF = 'Disconnects the bot and stops playback'

    @music.command(name='leave', aliases=['l', 'disconnect', 'dc'], help=LEAVE_HELP, brief=LEAVE_BRIEF)
    async def leave(self, ctx: Context):
        # TODO leave
        pass

    PLAY_HELP = 'Plays a YouTube url or search query. ' \
                'Calling this command with no arguments emulates the resume command'
    PLAY_BRIEF = 'Plays a url or search query'

    @music.command(name="play", aliases=[], help=PLAY_HELP, brief=PLAY_BRIEF)
    async def play(self, ctx: Context, *, url=''):
        # TODO play
        pass

    SKIP_HELP = 'Skips the current playback item and plays the next item in the queue'
    SKIP_BRIEF = 'Skips the current playback item'

    @music.command(name='skip', aliases=['next', 'n'], help=SKIP_HELP, brief=SKIP_BRIEF)
    async def skip(self, ctx: commands.Context):
        # TODO skip
        pass

    PAUSE_HELP = 'Pauses the current playback'

    @music.command(name='pause', aliases=['p'], help=PAUSE_HELP)
    async def pause(self, ctx: commands.Context):
        # TODO pause
        pass

    RESUME_HELP = 'Resumes the current playback'

    @music.command(name='resume', aliases=['r'], help=RESUME_HELP)
    async def resume(self, ctx: commands.Context):
        # TODO resume
        pass

    QUEUE_HELP = 'Prints the current playback queue'

    @music.command(name='queue', aliases=['q'], help=QUEUE_HELP)
    async def queue(self, ctx: commands.Context):
        # TODO queue
        pass

    # TODO remove cmd info

    @music.command(name='remove', aliases=['rm'])
    async def remove(self, ctx: commands.Context, idx: typing.Optional[int] = 0):
        # TODO remove
        pass
