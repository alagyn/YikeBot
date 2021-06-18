import wavelink
from discord.ext import commands
from discord.ext.commands import Context
import discord
import typing
import asyncio
from consts import MUSIC_LEAVE_TIME

OPTIONS = {
    "1️⃣": 0,
    "2⃣": 1,
    "3⃣": 2,
    "4⃣": 3,
    "5⃣": 4,
}


class MusicQueue:
    def __init__(self):
        self.queue = []

    def __len__(self):
        return len(self.queue)

    def __iter__(self):
        return self.queue.__iter__()

    def __getitem__(self, item):
        return self.queue[item]

    def clear(self):
        self.queue.clear()

    def __add__(self, other: typing.Union[wavelink.Track, wavelink.TrackPlaylist]):
        if isinstance(other, wavelink.Track):
            self.queue.append(other)
        elif isinstance(other, wavelink.TrackPlaylist):
            for x in other.tracks:
                self.queue.append(x)
        else:
            raise TypeError(f'Not a Track: {type(other)}')

    def isEmpty(self):
        return len(self.queue) == 0

    @property
    def first(self) -> wavelink.Track:
        if len(self.queue) > 0:
            return self.queue[0]
        else:
            raise IndexError('Cannot get first, queue is empty')

    def pop(self, idx=0) -> wavelink.Track:
        if len(self.queue) > 0:
            return self.queue.pop(idx)
        else:
            raise IndexError('Cannot pop, queue is empty')


class MusicPlayer(wavelink.Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.queue = MusicQueue()
        self.currentTimer = None
        self.currentCtx = None

    async def teardown(self):
        try:
            await self.destroy()
        except KeyError:
            pass

    async def sendNowPlaying(self, ctx: Context):

        track: wavelink.Track = self.queue.first
        embed = discord.Embed(
            title="Now Playing",
            description=f'{track.title}'
        )

        embed.set_thumbnail(url=track.thumb)
        await ctx.send(embed=embed)

    async def addTrack(self, ctx: Context, tracks):
        if not tracks:
            raise commands.UserInputError("No results found")

        if isinstance(tracks, wavelink.TrackPlaylist):
            self.queue + tracks
            embed = discord.Embed(title=f'Added {len(tracks.tracks)} tracks to queue')
            await ctx.send(embed=embed)
        else:
            if len(tracks) == 1:
                track = tracks[0]
            else:
                track = await self.chooseTrack(ctx, tracks)

            if track is None:
                return

            self.queue + track

            if len(self.queue) != 1:
                embed = discord.Embed(
                    title='Added To Queue:',
                    description=track.title
                )
                await ctx.send(embed=embed)

        if not self.is_playing and not self.queue.isEmpty():
            await self.startPlayback(ctx)

    async def chooseTrack(self, ctx: Context, tracks: typing.List[wavelink.Track]) -> \
            typing.Union[wavelink.Track, None]:

        embed = discord.Embed(
            title="Choose a result",
            description=f''.join(f'{i + 1}: "{x.title}"\n' for i, x in enumerate(tracks[:5]))
        )

        msg = await ctx.send(embed=embed)

        size = min(5, len(tracks))

        for emoji in list(OPTIONS.keys())[:size]:
            await msg.add_reaction(emoji)

        def msgCheck(r: discord.Reaction, u: discord.User):
            return r.message.id == msg.id and r.emoji in OPTIONS.keys() and u == ctx.author

        try:
            reaction, _ = await self.bot.wait_for('reaction_add', timeout=60, check=msgCheck)
        except asyncio.TimeoutError:
            await msg.delete()
            await ctx.message.delete()
            return None
        else:
            await msg.delete()
            return tracks[OPTIONS[reaction.emoji]]

    async def startPlayback(self, ctx):
        if self.currentCtx is None:
            self.currentCtx = ctx

        if self.currentTimer is not None:
            self.currentTimer.cancel()
            self.currentTimer = None

        if self.queue.isEmpty():
            print('Err: Queue is empty')
            return

        await self.sendNowPlaying(ctx)
        await self.play(self.queue.first)

    async def printQueue(self, ctx: Context):
        if self.queue.isEmpty():
            embed = discord.Embed(
                title='Play Queue Is Empty'
            )
        else:
            embed = discord.Embed(
                title='Now Playing',
                description=f'{self.queue.first.title}'
            )

            if len(self.queue) > 1:
                embed.add_field(name='Play Queue',
                                value=f''.join(f'{i + 1}: "{x.title}"\n' for i, x in enumerate(self.queue[1:])))

        await ctx.send(embed=embed)

    async def remove(self, ctx: Context, idx: int):
        if 0 < idx < len(self.queue):
            track = self.queue.pop(idx)

            embed = discord.Embed(
                title='Removed:',
                description=track.title
            )

            await ctx.send(embed=embed)
        else:
            raise commands.UserInputError('Invalid queue position')

    async def advance(self):
        try:
            self.queue.pop()
        except IndexError:
            # TODO raise error?
            pass

        if self.queue.isEmpty():
            await self.startTimeout()
        else:
            if self.currentCtx is None:
                # TODO raise error?
                pass

            await self.startPlayback(self.currentCtx)

    async def startTimeout(self):
        if self.currentTimer is not None:
            self.currentTimer.cancel()
        self.currentTimer = asyncio.create_task(self.waitForTimeout())

    async def waitForTimeout(self):
        await asyncio.sleep(MUSIC_LEAVE_TIME)
        if not self.is_playing:
            await self.destroy()

    def isEmpty(self):
        return self.queue.isEmpty()

