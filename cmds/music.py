# music.py
from discord.ext import commands
import discord
import youtube_dl
import asyncio
import typing

import yikeSnake

from consts import PAUSE_ICON, PLAY_ICON, THUMBS_UP

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
    'default_search': 'auto',
    'source_address': '0.0.0.0',  # bind to ipv4 since ipv6 addresses cause issues sometimes,
    'keepvideo': False,
    'skip_download': True,
    'hls_use_mpegts': True,
    'nopart': True
}

# TODO enable loglevel
ffmpeg_options = {
    # 'options': '-vn -loglevel fatal'
    'options': '-vn',
    'before_options': " -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -multiple_requests 1"
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        print(filename)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


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
        print("Unload: checking for vc")
        if self.vc is not None:
            print("Unload: creating task")
            self.bot.loop.create_task(self.disconnectFromVoice())
        print("Unload: done")

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
        print("Discon: checking vc")
        if self.vc is not None:
            print("Discon: stopping")
            self.vc.stop()
            print("Discon: disconnecting")
            await self.vc.disconnect()
            self.vc = None
            self.player = None
            self.playQueue = []
            self.send = None
            print("Discon: done")


    async def sendNowPlaying(self, ctx=None):
        out = f"Now Playing: ```{self.player.title}```"

        if ctx is not None:
            await ctx.send(out)
        elif self.send is not None:
            await self.send(out)

    async def makePlayer(self, url):
        return await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)

    PLAY_HELP = 'Plays a YouTube url or search query. ' \
                'Calling this command with no arguments emulates the resume command'
    PLAY_BRIEF = 'Plays a url or search query'

    @music.command(name="play", aliases=[], help=PLAY_HELP, brief=PLAY_BRIEF)
    async def play(self, ctx: commands.Context, *, url=''):
        print("Play: acquiring mutex")
        async with self.mutex:
            print("Play: mutex acquired")
            if len(url.strip()) == 0:
                if self.vc is not None and self.vc.is_paused():
                    await self.resume(ctx)
                    return
                else:
                    await ctx.send("Please provide a url or search term")

            if ctx.voice_client is None:
                try:
                    await Music.connectToChannel(ctx)
                except commands.CommandError:
                    return

            if self.player is None:
                print("Play: playing url")
                self.player = await self.makePlayer(url)
                self.vc = ctx.voice_client
                self.vc.play(self.player, after=self.afterPlay)
                self.send = ctx.send
                await self.sendNowPlaying(ctx)
            else:
                print("Play: adding to queue")
                p = await self.makePlayer(url)
                self.playQueue.insert(len(self.playQueue), p)
                await ctx.send(f"Queued: ```{p.title}```")

        print("Play: done")

    def afterPlay(self, e):
        if e is not None:
            print(e)
            return

        print("After: acquiring")
        asyncio.run_coroutine_threadsafe(self.mutex.acquire(), self.bot.loop).result()
        print("After: executing")
        if self.vc is not None and self.vc.is_connected() and len(self.playQueue) > 0:
            self.player = self.playQueue.pop(0)
            self.vc.play(self.player, after=self.afterPlay)

            asyncio.run_coroutine_threadsafe(self.sendNowPlaying(), self.bot.loop).result()

        else:
            self.player = None

        print("After: releasing")
        self.mutex.release()
        print(f"After: done, locked: {self.mutex.locked()}")

    SKIP_HELP = 'Skips the current playback item and plays the next item in the queue'
    SKIP_BRIEF = 'Skips the current playback item'

    @music.command(name='skip', aliases=['next', 'n'], help=SKIP_HELP, brief=SKIP_BRIEF)
    async def skip(self, ctx: commands.Context):
        async with self.mutex:
            if self.vc is not None:
                print("Skip: stopping")
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
            out = ''
            if self.player is not None:
                out += f'Now Playing: ```{self.player.title}```'

            size = len(self.playQueue)
            if size > 0:
                out += 'Play Queue: ```'
                for x in range(size):
                    out += f'{x + 1}: {self.playQueue[x].title}'
                    if x < size - 1:
                        out += '\n'

                out += ' ``` '

            if len(out) != 0:
                await ctx.send(out)
            else:
                await ctx.send("Nothing is playing")

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
