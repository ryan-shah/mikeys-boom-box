import discord
from discord.ext import commands
import asyncio
import itertools
import sys
import traceback

from YTDLSource import YTDLSource
from MusicPlayer import MusicPlayer
from constants import MESSAGE_TIMEOUT


class VoiceConnectionError(commands.CommandError):
    """Custom Exception class for connection errors."""


class InvalidVoiceChannel(VoiceConnectionError):
    """Exception for cases of invalid Voice Channels."""


class Music(commands.Cog):
    """Music related commands."""

    __slots__ = ("bot", "players")

    def __init__(self, bot):
        self.bot = bot
        self.players = {}

    async def cleanup(self, guild):
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass

        try:
            del self.players[guild.id]
        except KeyError:
            pass

    async def __local_check(self, ctx):
        """A local check which applies to all commands in this cog."""
        if not ctx.guild:
            raise commands.NoPrivateMessage
        return True

    async def __error(self, ctx, error):
        """A local error handler for all errors arising from commands in this cog."""
        if isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.send(
                    "This command can not be used in Private Messages."
                )
            except discord.HTTPException:
                pass
        elif isinstance(error, InvalidVoiceChannel):
            await ctx.send(
                "Error connecting to Voice Channel. "
                "Please make sure you are in a valid channel or provide me with one"
            )

        print("Ignoring exception in command {}:".format(ctx.command), file=sys.stderr)
        traceback.print_exception(
            type(error), error, error.__traceback__, file=sys.stderr
        )

    def get_player(self, ctx):
        """Retrieve the guild player, or generate one."""
        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            player = MusicPlayer(ctx)
            self.players[ctx.guild.id] = player

        return player

    @commands.command(name="connect", aliases=["join"])
    async def connect_(self, ctx, *, channel: discord.VoiceChannel = None):
        """Connect to voice.
        Parameters
        ------------
        channel: discord.VoiceChannel [Optional]
            The channel to connect to. If a channel is not specified, an attempt to join the voice channel you are in
            will be made.
        This command also handles moving the bot to different channels.
        """
        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                raise InvalidVoiceChannel(
                    "No channel to join. Please either specify a valid channel or join one."
                )

        vc = ctx.voice_client

        if vc:
            if vc.channel.id == channel.id:
                return
            try:
                await vc.move_to(channel)
            except asyncio.TimeoutError:
                raise VoiceConnectionError(f"Moving to channel: <{channel}> timed out.")
        else:
            try:
                await channel.connect()
            except asyncio.TimeoutError:
                raise VoiceConnectionError(
                    f"Connecting to channel: <{channel}> timed out."
                )

        await ctx.send(f"Connected to: **{channel}**", delete_after=MESSAGE_TIMEOUT)

    @commands.command(name="play", aliases=["sing", "p"])
    async def play_(self, ctx, *, search: str):
        """Request a song and add it to the queue.
        This command attempts to join a valid voice channel if the bot is not already in one.
        Uses YTDL to automatically search and retrieve a song.
        Parameters
        ------------
        search: str [Required]
            The song to search and retrieve using YTDL. This can be one of the following options
            - A search term
            - A link to a youtube video
            - A link to a youtube playlist
            - A link to a spotify song
            - A link to a spotify playlist
        """
        await ctx.typing()
        vc = ctx.voice_client

        if not vc:
            await ctx.invoke(self.connect_)

        # check if is a spotify link
        if "spotify" in search:
            await self.playSpotify(ctx, search)
        else:
            await self.playYTDL(ctx, search)

    async def playYTDL(self, ctx, search: str):
        player = self.get_player(ctx)

        sources = await YTDLSource.create_source(ctx, search, loop=self.bot.loop)

        for source in sources:
            await player.queue.put(source)
        if len(sources) > 1:
            await ctx.send(
                f"```ini\n[Added {len(sources)} songs to the Queue.]\n```",
                delete_after=15,
            )
        else:
            title = sources[0]["title"]
            await ctx.send(
                f"```ini\n[Added {title} to the Queue.]\n```",
                delete_after=MESSAGE_TIMEOUT,
            )

    async def playSpotify(self, ctx, search: str):
        player = self.get_player(ctx)

        if "playlist" in search:
            playlist = player.sp.playlist(search)
            for song in playlist["tracks"]["items"]:
                lookup = (
                    song["track"]["name"] + " by " + song["track"]["artists"][0]["name"]
                )
                sources = await YTDLSource.create_source(
                    ctx, lookup, loop=self.bot.loop
                )
                await player.queue.put(sources[0])
            lenList = playlist["tracks"]["total"]
            await ctx.send(
                f"Added {lenList} tracks to the queue", delete_after=MESSAGE_TIMEOUT
            )
        else:
            song = player.sp.track(search)
            lookup = song["name"] + " by " + song["artists"][0]["name"]
            sources = await YTDLSource.create_source(ctx, lookup, loop=self.bot.loop)
            await player.queue.put(sources[0])
            title = sources[0]["title"]
            await ctx.send(
                f"```ini\n[Added {title} to the Queue.]\n```",
                delete_after=MESSAGE_TIMEOUT,
            )

    @commands.command(name="pause")
    async def pause_(self, ctx):
        """Pause the currently playing song."""
        vc = ctx.voice_client

        if not vc or not vc.is_playing():
            return await ctx.send(
                "I am not currently playing anything!", delete_after=MESSAGE_TIMEOUT
            )
        elif vc.is_paused():
            return

        vc.pause()
        await ctx.send(f"**`{ctx.author}`**: Paused the song!")

    @commands.command(name="resume")
    async def resume_(self, ctx):
        """Resume the currently paused song."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send(
                "I am not currently playing anything!", delete_after=MESSAGE_TIMEOUT
            )
        elif not vc.is_paused():
            return

        vc.resume()
        await ctx.send(f"**`{ctx.author}`**: Resumed the song!")

    @commands.command(name="skip")
    async def skip_(self, ctx):
        """Skip the song."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send(
                "I am not currently playing anything!", delete_after=MESSAGE_TIMEOUT
            )

        if vc.is_paused():
            pass
        elif not vc.is_playing():
            return

        vc.stop()
        await ctx.send(f"**`{ctx.author}`**: Skipped the song!")

    @commands.command(name="queue", aliases=["q", "playlist"])
    async def queue_info(self, ctx):
        """Retrieve a basic queue of upcoming songs."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send(
                "I am not currently connected to voice!", delete_after=MESSAGE_TIMEOUT
            )

        player = self.get_player(ctx)
        if player.queue.empty():
            return await ctx.send("There are currently no more queued songs.")

        # Grab up to 5 entries from the queue...
        upcoming = list(itertools.islice(player.queue._queue, 0, 5))

        fmt = "\n".join(f'**`{_["title"]}`**' for _ in upcoming)
        embed = discord.Embed(title=f"Upcoming - Next {len(upcoming)}", description=fmt)

        await ctx.send(embed=embed)

    @commands.command(
        name="now_playing", aliases=["np", "current", "currentsong", "playing"]
    )
    async def now_playing_(self, ctx):
        """Display information about the currently playing song."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send(
                "I am not currently connected to voice!", delete_after=MESSAGE_TIMEOUT
            )

        player = self.get_player(ctx)
        if not player.current:
            return await ctx.send("I am not currently playing anything!")

        try:
            # Remove our previous now_playing message.
            await player.np.delete()
        except discord.HTTPException:
            pass

        player.np = await ctx.send(
            f"**Now Playing:** `{vc.source.title}` "
            f"requested by `{vc.source.requester}`"
        )

    @commands.command(name="volume", aliases=["vol"])
    async def change_volume(self, ctx, *, vol: float):
        """Change the player volume.
        Parameters
        ------------
        volume: float or int [Required]
            The volume to set the player to in percentage. This must be between 1 and 100.
        """
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send(
                "I am not currently connected to voice!", delete_after=MESSAGE_TIMEOUT
            )

        if not 0 < vol < 101:
            return await ctx.send("Please enter a value between 1 and 100.")

        player = self.get_player(ctx)

        if vc.source:
            vc.source.volume = vol / 100

        player.volume = vol / 100
        await ctx.send(f"**`{ctx.author}`**: Set the volume to **{vol}%**")

    @commands.command(name="stop")
    async def stop_(self, ctx):
        """Stop the currently playing song and destroy the player.
        !Warning!
            This will destroy the player assigned to your guild, also deleting any queued songs and settings.
        """
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send(
                "I am not currently playing anything!", delete_after=MESSAGE_TIMEOUT
            )

        await self.cleanup(ctx.guild)

    @commands.command(name="shuffle")
    async def shuffle_(self, ctx):
        """Shuffle the music in the queue"""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send(
                "I am not currently playing anything!", delete_after=MESSAGE_TIMEOUT
            )
        player = self.get_player(ctx)
        player.shuffle()
        await ctx.send("Queue has been shuffled!", delete_after=MESSAGE_TIMEOUT)
        await ctx.invoke(self.queue_info)

    @commands.command(name="trae")
    async def trae_(self, ctx):
        """Reacts to one of Trae's jokes"""
        await ctx.typing()

        vc = ctx.voice_client

        if not vc:
            await ctx.invoke(self.connect_)

        return await self.playYTDL(ctx, "https://www.youtube.com/watch?v=iYVO5bUFww0")
