from discord.ext import commands
from MusicCog import Music
from constants import DISCORD_API_TOKEN

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"),
    description="Relatively simple music bot example",
)


@bot.event
async def on_ready():
    print("We have logged in as {0}".format(bot.user.name))
    cog = bot.get_cog("Music")
    print([c.qualified_name for c in cog.walk_commands()])


bot.add_cog(Music(bot))
bot.run(DISCORD_API_TOKEN)
