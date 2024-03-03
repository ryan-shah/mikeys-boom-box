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
querystring = {"url":"https://www.tiktok.com/@tiktok/video/7231338487075638570","hd":"1"}
temp_filename = "tmp_tok.mp4"

class TikTok(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.content.startswith("!"):
            return
        url = ""
        print("tok triggered on " + message.content)
        for word in message.content.split(" "):
            if "tiktok.com" in word:
                url = word
                print("found tiktok - " + url)
        if url != "":
            querystring["url"]=url
            print("hitting api")
            api_response = requests.get(api, headers=headers, params=querystring)
            metadata = api_response.json()
            video = requests.get(metadata["data"]["hdplay"], stream=True)
            print("downloading video")
            with open(temp_filename, "wb") as f:
                for chunk in video.iter_content(chunk_size = 1024*1024):
                    if chunk:
                        f.write(chunk)
            print("sending response")
            await message.reply(file=File(temp_filename, filename="tiktok_file.mp4"))
            print("removing file")
            os.remove(temp_filename)