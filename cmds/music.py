# music.py
from discord.ext import commands
import discord
import youtube_dl
import asyncio

import yikeSnake

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
    'source_address': '0.0.0.0'  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn -loglevel fatal'
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

    # TODO join help info
    @commands.command(name="join", aliases=['j'], help="Joins the bot to your currentt voice channel")
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

    # TODO leave cmd info
    @commands.command(name='leave', aliases=['l', 'exit', 'yeet'])
    async def leave(self, ctx: commands.Context):
        if self.vc is not None:
            self.vc.stop()
            self.vc = None
        await ctx.guild.change_voice_state(channel=None)

    @commands.command(name="play", aliases=['p'], help=PLAY_DESC, brief=PLAY_BRIEF, usage=PLAY_USAGE)
    async def play(self, ctx: commands.Context, *, url: str):
        if len(url) == 0:
            await ctx.send("Please provide a Youtube URL")
            return

        self.player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
        self.vc = ctx.voice_client
        self.vc.play(self.player, after=lambda e: print('Player error: %s' % e) if e else None)
        await ctx.send(f"Now Playing: ```{self.player.title}```")

    @play.before_invoke
    async def ensure_voice(self, ctx: commands.Context):
        await self.join(ctx)


def setup(bot):
    bot.add_cog(Music(bot))
