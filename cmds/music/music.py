# music.py
from discord.ext import commands
from discord.ext.commands import Context
import discord
import asyncio
import os
import wavelink
import typing
import re

from yikeSnake import YikeSnake
from .musicPlayer import MusicPlayer

from consts import PAUSE_ICON, PLAY_ICON, THUMBS_UP

URL_REGEX = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
URL_PATTERN = re.compile(URL_REGEX)

SEEK_PATTERN = re.compile(r'(?P<delta>[+-])?((?P<min>\d*):(?P<sec>\d{2})|(?P<allsec>\d+))')


class NotInVoice(commands.CommandError):
    pass


def setup(bot: YikeSnake):
    bot.add_cog(Music(bot))


class Music(commands.Cog, wavelink.WavelinkMixin):
    def __init__(self, bot: YikeSnake):
        self.bot = bot
        self.wl = wavelink.Client(bot=bot)

        self.playing = False

        host = os.getenv('LAVA_SERVER')
        port = os.getenv('LAVA_PORT')

        self.node = {
            'host': host,
            'port': port,
            'rest_uri': f'http://{host}:{port}',
            'password': os.getenv('LAVA_PASS'),
            'identifier': os.getenv('LAVA_ID'),
            'region': os.getenv("LAVA_REGION")
        }

        bot.loop.create_task(self.setup())

        self.timeoutCount = 0

    async def cog_command_error(self, ctx: Context, error):
        if isinstance(error, commands.UserInputError):
            await ctx.send(str(error))

    @wavelink.WavelinkMixin.listener()
    async def on_node_ready(self, node: wavelink.Node):
        self.bot.addAdminLog(f'Wavelink node "{node.identifier}" ready')

    # TODO have error functions?
    @wavelink.WavelinkMixin.listener("on_track_stuck")
    @wavelink.WavelinkMixin.listener("on_track_end")
    @wavelink.WavelinkMixin.listener("on_track_exception")
    async def onPlayerStop(self, node, payload):
        # print('onPlayerStop')
        await payload.player.advance(None, False)

    async def setup(self):
        await self.bot.wait_until_ready()
        await self.wl.initiate_node(**self.node)

    def cog_unload(self):
        self.bot.loop.create_task(self.close())

    async def close(self):
        await self.wl.destroy_node(identifier=self.node['identifier'])
        for k, v in self.wl.players.items():
            v.destroy()
        del self.wl

    MUSIC_HELP = 'Commands to play music in a voice channel, calling with no sub command activates the play command'
    MUSIC_BRIEF = 'Commands to play music'

    @commands.group(name='music', aliases=['m'], invoke_without_command=True, help=MUSIC_HELP, brief=MUSIC_BRIEF)
    async def music(self, ctx: Context, *, args=''):
        await self.play(ctx, query=args)

    JOIN_HELP = 'Connects the bot to your current voice channel'

    def getPlayer(self, ctx: Context) -> MusicPlayer:
        # noinspection PyTypeChecker
        return self.wl.get_player(ctx.guild.id, cls=MusicPlayer, context=ctx)

    @music.command(name='join', aliases=['j', 'connect', 'c'], help=JOIN_HELP)
    async def join(self, ctx: Context):
        if ctx.author.voice is not None:
            channel: discord.VoiceChannel = ctx.author.voice.channel
            await self.getPlayer(ctx).connect(channel.id)
        else:
            raise commands.UserInputError('Not in a voice channel')

    LEAVE_HELP = 'Disconnects the bot and stops playback. Clears the playback queue'
    LEAVE_BRIEF = 'Disconnects the bot and stops playback'

    @music.command(name='leave', aliases=['l', 'disconnect', 'dc', 'stop'], help=LEAVE_HELP, brief=LEAVE_BRIEF)
    async def leave(self, ctx: Context):
        player = self.getPlayer(ctx)
        player.cancelTimer()
        await player.destroy()


    PLAY_HELP = 'Plays a YouTube url or search query. ' \
                'Calling this command with no arguments emulates the resume command'
    PLAY_BRIEF = 'Plays a url or search query'

    @music.command(name="play", aliases=[], help=PLAY_HELP, brief=PLAY_BRIEF)
    async def play(self, ctx: Context, *, query: typing.Optional[str]):
        player = self.getPlayer(ctx)

        if not player.is_connected:
            await self.join(ctx)

        if query is None:
            if len(player.queue) == 0:
                raise commands.UserInputError("Play queue is empty")

            if player.is_paused:
                await player.set_pause(False)
                await ctx.message.add_reaction(PLAY_ICON)

            return

        query = query.strip("<>")
        if not URL_PATTERN.match(query):
            query = f'ytsearch:{query}'

        await player.addTrack(ctx, await self.wl.get_tracks(query))

    SKIP_HELP = 'Skips the current playback item and plays the next item in the queue'
    SKIP_BRIEF = 'Skips the current playback item'

    @music.command(name='skip', aliases=['next', 'n'], help=SKIP_HELP, brief=SKIP_BRIEF)
    async def skip(self, ctx: commands.Context):
        player = self.getPlayer(ctx)
        await player.advance(ctx, True)

    PAUSE_HELP = 'Pauses the current playback'

    @music.command(name='pause', aliases=['p'], help=PAUSE_HELP)
    async def pause(self, ctx: commands.Context):
        player = self.getPlayer(ctx)

        if not player.is_paused:
            await player.set_pause(True)

        await ctx.message.add_reaction(PAUSE_ICON)

    RESUME_HELP = 'Resumes the current playback'

    @music.command(name='resume', aliases=['r'], help=RESUME_HELP)
    async def resume(self, ctx: commands.Context):
        player = self.getPlayer(ctx)
        if player.is_paused:
            await player.set_pause(False)

        await ctx.message.add_reaction(PLAY_ICON)

    QUEUE_HELP = 'Prints the current playback queue'

    @music.command(name='queue', aliases=['q'], help=QUEUE_HELP)
    async def queue(self, ctx: commands.Context):
        await self.getPlayer(ctx).printQueue(ctx)

    REMOVE_HELP = 'Removes the given item from the queue'

    @music.command(name='remove', aliases=['rm'], help=REMOVE_HELP)
    async def remove(self, ctx: commands.Context, idx: typing.Optional[int] = 0):
        await self.getPlayer(ctx).remove(ctx, idx)

    SHUFFLE_HELP = 'Shuffles the unplayed queue'

    @music.command(name='shuffle', aliases=['shuf'], help=SHUFFLE_HELP)
    async def shuffle(self, ctx: commands.Context):
        await self.getPlayer(ctx).shuffle(ctx)

    JUMP_HELP = 'Jumps to a specific item in the queue'

    @music.command(name='jump', help=JUMP_HELP)
    async def jump(self, ctx: commands.Context, idx: int):
        player = self.getPlayer(ctx)

        if 0 <= idx < len(player.queue):
            player.queue.curIdx = idx - 1
            await player.advance(ctx, True)
        else:
            # TODO error?
            pass

    SEEK_HELP = 'Seeks to a specific timestamp or time delta'

    @music.command(name='seek', help=SEEK_HELP)
    async def seek(self, ctx: commands.Context, seektime: str):

        player = self.getPlayer(ctx)

        if not player.actually_playing:
            return

        match = SEEK_PATTERN.fullmatch(seektime.strip())
        if match is None:
            raise commands.UserInputError("Invalid time format, try [+-][min:]sec")

        mins = match.group('min')
        if mins is not None:
            seekpos = (60 * int(mins) + int(match.group('sec'))) * 1000
        else:
            seekpos = int(match.group('allsec')) * 1000


        curpos = int(player.position)

        delta = match.group('delta')
        if delta is not None:

            if delta == '+':
                seekpos += curpos
            else:
                seekpos = curpos - seekpos

        seekpos = max(0, seekpos)

        await player.seek(seekpos)
        await ctx.message.add_reaction(THUMBS_UP)

    @music.command(name='loop')
    async def loop(self, ctx: commands.Context):
        p = self.getPlayer(ctx)
        if p is None:
            return
        p.loop = not p.loop

        if p.loop:
            await ctx.send('Looping Started')
        else:
            await ctx.send('Looping Ended')
