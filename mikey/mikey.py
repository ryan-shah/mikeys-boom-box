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


@mikey.event
async def on_message(message):
    search = "i'm "
    if search in message.content.lower():
        msg = message.content
        start = msg.lower().index(search) + 4
        end = len(msg)
        if '.' in msg:
            idx = msg.index('.')
            if idx > start:
                end = idx
        if ',' in msg:
            idx = msg.index('.')
            if idx > start and idx < end:
                end = idx
        response = "Hi " + msg[start:end] + ", I thought you were <@" + str(message.author.id) + ">."
        await message.reply(response)

mikey.add_cog(Music(mikey))
mikey.run(DISCORD_API_TOKEN)
