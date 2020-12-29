# music.py
from discord.ext import commands
import discord
import youtube_dl
import asyncio
import typing

import yikeSnake

from consts import PAUSE_ICON, PLAY_ICON, THUMBS_UP

OPTIONS = {
    "1️⃣": 0,
    "2⃣": 1,
    "3⃣": 2,
    "4⃣": 3,
    "5⃣": 4,
}

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': True,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'ytsearch:',
    'source_address': '0.0.0.0',  # bind to ipv4 since ipv6 addresses cause issues sometimes,
}

# TODO enable loglevel
ffmpeg_options = {
    # 'options': '-vn -loglevel fatal'
    'options': '-vn',
    'before_options': " -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -multiple_requests 1"
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLException(Exception):
    pass


class YTDLSource(discord.PCMVolumeTransformer):

    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def choose_track(cls, ctx: commands.Context, tracks):

        if len(tracks) > 1:
            embed = discord.Embed(
                title='Choose A Result',
                description=f''.join(f'{i + 1}: "{x["title"]}"\n' for i, x in enumerate(tracks[:5]))
            )

            msg = await ctx.send(embed=embed)
            size = min(5, len(tracks))

            for emoji in list(OPTIONS.keys())[:size]:
                await msg.add_reaction(emoji)

            def msgCheck(r: discord.Reaction, u: discord.User):
                return r.message.id == msg.id and r.emoji in OPTIONS.keys() and u == ctx.author

            try:
                reaction, _ = await ctx.bot.wait_for('reaction_add', timeout=60, check=msgCheck)
            except asyncio.TimeoutError:
                await msg.delete()
                await ctx.message.delete()
                return None
            else:
                await msg.delete()
                return tracks[OPTIONS[reaction.emoji]]
        else:
            return tracks[0]


    @classmethod
    async def from_url(cls, ctx: commands.Context, query, *, loop=None):
        # TODO update exception msgs

        loop = loop or asyncio.get_event_loop()

        # Process the query
        processedInfo = ytdl.extract_info(query, download=False)

        if processedInfo is None:
            raise YTDLException("Cannot fetch video")

        track = None
        if 'entries' in processedInfo:
            tracks = processedInfo['entries']
            if len(tracks) > 0:
                track = await cls.choose_track(ctx, tracks)

        if track is None:
            track = processedInfo

        return cls(discord.FFmpegPCMAudio(track['url'], **ffmpeg_options), data=track)


class Music(commands.Cog):
    # TODO implement clear command capabilities

    def __init__(self, bot: yikeSnake.YikeSnake):
        self.bot: yikeSnake.YikeSnake = bot
        self.previousMsgs = []
        self.player = None
        self.vc = None
        self.playQueue = []
        self.send = None

        self.mutex = asyncio.Lock(loop=self.bot.loop)

    def cog_unload(self):
        if self.vc is not None:
            self.bot.loop.create_task(self.disconnectFromVoice())

    async def cog_command_error(self, ctx: commands.Context, error):
        if ctx.command is self.join or ctx.command is self.play:
            return
        else:
            raise error

    MUSIC_HELP = 'Commands to play music in a voice channel, calling with no sub command activates the play command'
    MUSIC_BRIEF = 'Commands to play music'

    @commands.group(name='music', aliases=['m'], invoke_without_command=True, help=MUSIC_HELP, brief=MUSIC_BRIEF)
    async def music(self, ctx: commands.Context, *, args=''):
        await self.play(ctx, url=args)

    JOIN_HELP = 'Connects the bot to your current voice channel'

    @music.command(name="join", aliases=['j'], help=JOIN_HELP)
    async def join(self, ctx: commands.Context):
        async with self.mutex:
            await Music.connectToChannel(ctx)

    @staticmethod
    async def connectToChannel(ctx: commands.context):
        if ctx.author.voice is not None:
            channel = ctx.author.voice.channel
            if ctx.voice_client is None:
                await channel.connect()
            else:
                await ctx.voice_client.move_to(channel)

            await ctx.guild.change_voice_state(channel=channel, self_deaf=True)
        else:
            await ctx.send("You must be in a voice channel to use this command")
            raise commands.CommandError("Not in a voice channel")

    LEAVE_HELP = 'Disconnects the bot and stops playback. Clears the playback queue'
    LEAVE_BRIEF = 'Disconnects the bot and stops playback'

    @music.command(name='leave', aliases=['l', 'exit', 'yeet', 'stop'], help=LEAVE_HELP, brief=LEAVE_BRIEF)
    async def leave(self, ctx: commands.Context = None):
        async with self.mutex:
            await self.disconnectFromVoice()

    async def disconnectFromVoice(self):
        if self.vc is not None:
            self.vc.stop()
            await self.vc.disconnect()
            self.vc = None
            self.player = None
            self.playQueue = []
            self.send = None

    async def sendNowPlaying(self, ctx=None):

        embed = discord.Embed(
            title='Now Playing',
            description=self.player.title
        )

        if ctx is not None:
            await ctx.send(embed=embed)
        elif self.send is not None:
            await self.send(embed=embed)

    async def makePlayer(self, ctx, url):
        return await YTDLSource.from_url(url, ctx, loop=self.bot.loop)

    PLAY_HELP = 'Plays a YouTube url or search query. ' \
                'Calling this command with no arguments emulates the resume command'
    PLAY_BRIEF = 'Plays a url or search query'

    @music.command(name="play", aliases=[], help=PLAY_HELP, brief=PLAY_BRIEF)
    async def play(self, ctx: commands.Context, *, url=''):
        async with self.mutex:
            if len(url.strip()) == 0:
                if self.vc is not None and self.vc.is_paused():
                    self.vc.resume()
                    await ctx.message.add_reaction(PLAY_ICON)
                    return
                else:
                    await ctx.send("Please provide a url or search term")

            if ctx.voice_client is None:
                try:
                    await Music.connectToChannel(ctx)
                except commands.CommandError:
                    return

            if self.player is None:
                self.player = await self.makePlayer(url, ctx)
                self.vc = ctx.voice_client
                self.vc.play(self.player, after=self.afterPlay)
                self.send = ctx.send
                await self.sendNowPlaying(ctx)
            else:
                p = await self.makePlayer(url, ctx)
                self.playQueue.insert(len(self.playQueue), p)
                embed = discord.Embed(
                    title='Queued',
                    description=p.title
                )
                await ctx.send(embed=embed)

    def afterPlay(self, e):
        if e is not None:
            print(e)
            return

        asyncio.run_coroutine_threadsafe(self.mutex.acquire(), self.bot.loop).result()

        if self.vc is not None and self.vc.is_connected() and len(self.playQueue) > 0:
            self.player = self.playQueue.pop(0)
            self.vc.play(self.player, after=self.afterPlay)

            asyncio.run_coroutine_threadsafe(self.sendNowPlaying(), self.bot.loop).result()

        else:
            self.player = None

        self.mutex.release()

    SKIP_HELP = 'Skips the current playback item and plays the next item in the queue'
    SKIP_BRIEF = 'Skips the current playback item'

    @music.command(name='skip', aliases=['next', 'n'], help=SKIP_HELP, brief=SKIP_BRIEF)
    async def skip(self, ctx: commands.Context):
        async with self.mutex:
            if self.vc is not None:
                self.vc.stop()

    PAUSE_HELP = 'Pauses the current playback'

    @music.command(name='pause', aliases=['p'], help=PAUSE_HELP)
    async def pause(self, ctx: commands.Context):
        async with self.mutex:
            if self.vc is not None and self.vc.is_playing():
                self.vc.pause()
                await ctx.message.add_reaction(PAUSE_ICON)

    RESUME_HELP = 'Resumes the current playback'

    @music.command(name='resume', aliases=['r'], help=RESUME_HELP)
    async def resume(self, ctx: commands.Context):
        async with self.mutex:
            if self.vc is not None and self.vc.is_paused():
                self.vc.resume()
                await ctx.message.add_reaction(PLAY_ICON)

    QUEUE_HELP = 'Prints the current playback queue'

    @music.command(name='queue', aliases=['q'], help=QUEUE_HELP)
    async def queue(self, ctx: commands.Context):
        async with self.mutex:
            embed = discord.Embed()
            if self.player is not None:
                embed.add_field(name='Now Playing',
                                value=self.player.title,
                                inline=False)

            size = len(self.playQueue)
            if size > 0:
                q = ''
                for x in range(size):
                    q += f'{x + 1}: {self.playQueue[x].title}'
                    if x < size - 1:
                        q += '\n'

                embed.add_field(name='Queue:',
                                value=q)

            if len(embed.fields) == 0:
                embed = discord.Embed(title='Nothing Is Playing')

            await ctx.send(embed=embed)

    @music.command(name='remove', aliases=['rm'])
    async def remove(self, ctx: commands.Context, idx: typing.Optional[int] = 0):
        async with self.mutex:
            size = len(self.playQueue)
            if size > 0:
                if 0 <= idx <= size:
                    if idx < 1:
                        self.playQueue.pop(size - 1)
                    elif 1 <= idx <= size:
                        self.playQueue.pop(idx - 1)

                    await ctx.message.add_reaction(THUMBS_UP)
                else:
                    await ctx.send("Invalid index")
            else:
                await ctx.send("Queue is empty")


def setup(bot):
    bot.add_cog(Music(bot))
