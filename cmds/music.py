# music.py
from discord.ext import commands
import discord
import youtube_dl
import asyncio

import yikeSnake
import typing

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
    PLAY_DESC = 'Plays a youtube video'
    PLAY_BRIEF = "_play <video url>"
    PLAY_USAGE = "<video url>"

    def __init__(self, bot: yikeSnake.YikeSnake):
        self.bot: yikeSnake.YikeSnake = bot
        self.previousMsgs = []
        self.player = None
        self.vc = None
        self.queue = []
        self.send = None

    async def cog_command_error(self, ctx: commands.Context, error):
        if ctx.command is self.join or ctx.command is self.play:
            return
        else:
            raise error

    @commands.group(name='music', aliases=['m'], invoke_without_command=True)
    async def music(self, ctx: commands.Context, *, args=''):
        await self.play(ctx, url=args)

    # TODO join help info
    @music.command(name="join", aliases=['j'], help="Joins the bot to your current voice channel")
    async def join(self, ctx: commands.Context):
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

    # TODO leave cmd info
    @music.command(name='leave', aliases=['l', 'exit', 'yeet'])
    async def leave(self, ctx: commands.Context):
        if self.vc is not None:
            self.vc.stop()
            self.vc = None
            self.player = None
            self.queue = []
            self.send = None
        await ctx.guild.change_voice_state(channel=None)

    async def sendNowPlaying(self, ctx=None):
        out = f"Now Playing: ```{self.player.title}```"

        if ctx is not None:
            await ctx.send(out)
        elif self.send is not None:
            await self.send(out)

    async def makePlayer(self, url):
        return await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)

    @music.command(name="play", aliases=['p'], help=PLAY_DESC, brief=PLAY_BRIEF, usage=PLAY_USAGE)
    async def play(self, ctx: commands.Context, *, url=''):
        if len(url.strip()) == 0:
            await self.resume(ctx)
            return

        if ctx.voice_client is None:
            try:
                await self.join(ctx)
            except commands.CommandError:
                return

        if len(url) == 0:
            await ctx.send("Please provide a Youtube URL")
            return

        if self.player is None:
            self.player = await self.makePlayer(url)
            self.vc = ctx.voice_client
            self.vc.play(self.player, after=self.afterPlay)
            self.send = ctx.send
            await self.sendNowPlaying(ctx)
        else:
            p = await self.makePlayer(url)
            self.queue.insert(len(self.queue), p)
            await ctx.send(f"Queued: ```{p.title}```")

    def afterPlay(self, e):
        if e is not None:
            print(e)
            return

        if self.vc is not None and len(self.queue) > 0:
            self.player = self.queue.pop(0)
            self.vc.play(self.player, after=self.afterPlay)
            asyncio.run_coroutine_threadsafe(self.sendNowPlaying(), self.bot.loop)
        else:
            self.player = None

    # TODO skip cmd help info
    @music.command(name='skip', aliases=['next', 'n'])
    async def skip(self, ctx: commands.Context):
        if self.vc is not None:
            self.vc.stop()
            if len(self.queue) > 0:
                self.player = self.queue.pop(0)
                self.vc.play(self.player, after=self.afterPlay)
                await self.sendNowPlaying(ctx)

    # TODO pause cmd help info
    @music.command(name='pause', aliases=[])
    async def pause(self, ctx: commands.Context):
        if self.vc is not None and self.vc.is_playing():
            self.vc.pause()

    @music.command(name='resume')
    async def resume(self, ctx: commands.Context):
        if self.vc is not None and self.vc.is_paused():
            self.vc.resume()

    # TODO print queue


def setup(bot):
    bot.add_cog(Music(bot))
