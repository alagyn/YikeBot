import math

import wavelink
from discord.ext import commands
from discord.ext.commands import Context
import discord
import typing
import asyncio
from consts import MUSIC_LEAVE_TIME, SHUFFLE_ICON
from random import random

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
        self.curIdx = 0

    def __len__(self):
        return len(self.queue)

    def remaining(self) -> int:
        return len(self.queue) - self.curIdx - 1

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

    def hasCurrent(self) -> bool:
        return 0 <= self.curIdx < len(self.queue)

    def shuffle(self):
        if self.hasNext():
            for i in reversed(range(self.curIdx + 2, len(self.queue))):
                x = math.floor(random() * i + 1)
                self.queue[i], self.queue[x] = self.queue[x], self.queue[i]

    def hasNext(self) -> bool:
        return self.curIdx + 1 < len(self.queue)

    def next(self):
        self.curIdx += 1

    def current(self) -> wavelink.Track:
        return self.queue[self.curIdx]

    def pop(self, idx=0) -> wavelink.Track:
        if len(self.queue) > 0:
            return self.queue.pop(idx)
        else:
            raise IndexError('Cannot pop, queue is empty')


class MusicPlayer(wavelink.Player):
    # IDGEN = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.queue = MusicQueue()
        self.currentTimer = None
        self.currentCtx = None

        self.skipFlag = False

        # keeping track of is_playing myself because wavelink broke I guess
        self.actually_playing = False

        # self.id = MusicPlayer.IDGEN
        # MusicPlayer.IDGEN += 1
        # print('constr:', self.id)

        self.loop = False


    async def teardown(self):
        try:
            await self.destroy()
        except KeyError:
            pass

    async def sendNowPlaying(self, ctx: Context):

        track: wavelink.Track = self.queue.current()
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

            if self.queue.remaining() > 0 or self.actually_playing:
                embed = discord.Embed(
                    title='Added To Queue:',
                    description=track.title
                )
                await ctx.send(embed=embed)

        # print('playing?', self.actually_playing)
        if not self.is_paused and not self.actually_playing:
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

    def cancelTimer(self):
        if self.currentTimer is not None:
            self.currentTimer.cancel()
            self.currentTimer = None

    async def startPlayback(self, ctx):
        self.currentCtx = ctx

        self.cancelTimer()

        self.actually_playing = False

        try:
            # print(f'Cur IDX: {self.queue.curIdx}')
            # print(f'Playing : {self.queue.current().title}')
            await self.play(self.queue.current())
            await self.sendNowPlaying(ctx)

            self.actually_playing = True

        except IndexError:
            await self.startTimeout()
            # print('end of queue')

    async def printQueue(self, ctx: Context):
        if self.queue.isEmpty():
            embed = discord.Embed(
                title='Play Queue Is Empty'
            )
        else:
            embed = discord.Embed(
                title='Now Playing',
                description=f'{self.queue.current().title}'
            )

            # print('Remaining:', self.queue.remaining())
            if self.queue.remaining() > 0:
                nextQ = list(enumerate(self.queue))[self.queue.curIdx + 1:self.queue.curIdx + 11]
                embed.add_field(name='Play Queue',
                                value=f''.join(f'{i}: "{x.title}"\n' for i, x in nextQ))

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

    async def shuffle(self, ctx: Context):
        self.queue.shuffle()
        await ctx.message.add_reaction(SHUFFLE_ICON)

    async def advance(self, ctx: Context, manual: bool):
        if not self.is_connected:
            return

        # Hacked, onplayerstop will be called when a new song plays
        # This prevents this func from running twice when a user manually skips a track
        if not manual and self.skipFlag:
            self.skipFlag = False
            return
        elif manual:
            self.skipFlag = True
            await self.stop()

        if not self.loop or (self.loop and manual):
            self.queue.next()
        if ctx is not None:
            await self.startPlayback(ctx)
        else:
            await self.startPlayback(self.currentCtx)

    async def startTimeout(self):
        if self.currentTimer is not None:
            self.currentTimer.cancel()
        self.currentTimer = asyncio.create_task(self.waitForTimeout())

    async def waitForTimeout(self):
        await asyncio.sleep(MUSIC_LEAVE_TIME)
        if not self.actually_playing:
            await self.destroy()

    def isEmpty(self):
        return self.queue.isEmpty()
