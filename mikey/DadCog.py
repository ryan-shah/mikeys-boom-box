from discord.ext import commands


class Dad(commands.Cog):
    # https://www.cl.cam.ac.uk/~mgk25/ucs/quotes.html
    SINGLE_QUOTES = ["\u0027", "\u0060", "\u00B4", "\u2018", "\u2019"]

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.content.startswith("!"):
            return
        response = dadJoke(message)
        if response == "":
            return
        await message.reply(response)


def getNewName(search, msg):
    punct = [".", "!", "?", ","]

    msg = msg[msg.lower().index(search) + len(search) :]
    end = len(msg)
    start = 0

    for char in punct:
        if char in msg:
            idx = msg.index(char)
            if idx > start and idx < end:
                end = idx
    return msg[start:end]


def dadJoke(message):
    triggers = [f"i{single_quote}m " for single_quote in Dad.SINGLE_QUOTES] + [
        "i am ",
        " im ",
    ]
    for word in triggers:
        if word in message.content.lower():
            name = getNewName(word, message.content)
            response = (
                "Hi " + name + ", I thought you were <@" + str(message.author.id) + ">."
            )
            return response
    return ""
