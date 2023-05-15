from discord.ext import commands
from discord import __version__, Intents
from discord import __version__, Intents
from MusicCog import Music
from constants import DISCORD_API_TOKEN
from DadCog import Dad
from CalCog import Calendar
import asyncio

intents = Intents.default()
intents.message_content = True
intents.guild_scheduled_events = True

mikey = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"),
    description="Mikey's Magical Boombox",
    intents=intents
)


@mikey.event
async def on_ready():
    print("We have logged in as {0}".format(mikey.user.name))
    print(__version__)

async def main():
    await mikey.add_cog(Music(mikey))
    await mikey.add_cog(Dad(mikey))
    await mikey.add_cog(Calendar(mikey))
    await mikey.start(DISCORD_API_TOKEN)

asyncio.run(main())
asyncio.run(main())
