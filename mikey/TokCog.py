from discord.ext import commands
from discord import File
from constants import RAPID_API_KEY
import requests
import os

api = "https://tiktok-video-no-watermark2.p.rapidapi.com/"
headers = {
	"X-RapidAPI-Key": RAPID_API_KEY,
	"X-RapidAPI-Host": "tiktok-video-no-watermark2.p.rapidapi.com"
}
querystring = {"url":"https://www.tiktok.com/@tiktok/video/7231338487075638570"}
temp_filename = "tmp_tok.mp4"

class TikTok(commands.Cog):
    def __init__(self, bot):
        """        Initialize the class with a bot instance.

        Args:
            bot: The bot instance to be assigned.
        """

        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        """        Process the message and retrieve a TikTok video.

        This function processes the message to extract a TikTok video URL, retrieves the video metadata using an API,
        downloads the video, and sends it as a reply to the message.

        Args:
            message (str): The message content received.


        Raises:
            Exception: If there is an error in processing the video.
        """

        if message.author.bot or message.content.startswith("!"):
            return
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
        url = ""
        for word in message.content.split(" "):
            if "tiktok.com" in word:
                url = word
        if url != "":
            try:
                print("started process")
                querystring["url"]=url
                api_response = requests.get(api, headers=headers, params=querystring)
                metadata = api_response.json()
                if metadata["code"] != 0:
                    await message.reply(metadata["msg"])
                    return
                video = requests.get(metadata["data"]["play"], stream=True)
                with open(temp_filename, "wb") as f:
                    for chunk in video.iter_content(chunk_size = 1024*1024):
                        if chunk:
                            f.write(chunk)
                await message.reply(file=File(temp_filename, filename="tiktok_file.mp4"))
            except Exception as e:
                await message.reply("unable to process video: " + e.message)
            if os.path.exists(temp_filename):
                os.remove(temp_filename)