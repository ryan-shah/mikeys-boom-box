from discord.ext import commands
from MusicCog import Music
from constants import DISCORD_API_TOKEN

mikey = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"),
    description="Mikey's Magical Boombox",
)


@mikey.event
async def on_ready():
    print("We have logged in as {0}".format(mikey.user.name))


mikey.add_cog(Music(mikey))
mikey.run(DISCORD_API_TOKEN)
