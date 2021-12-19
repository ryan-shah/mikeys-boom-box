# Mikey's Boom Box
A pretty basic discord music bot

Plays songs from a youtube/spotify video/song or playlist.

Be warned, Mikey is a father and thinks he's funny.

## Prerequisites
You will need python3 and pip3 to run this project.

Linux install: `$ sudo apt-get install python3 python3-pip`

Windows/Mac install: See instructions [here](https://www.python.org/)

## Running Locally
1. Follow the steps [here](https://www.freecodecamp.org/news/create-a-discord-bot-with-python/) to create a discord bot account and add it to your server.
    - Make sure the bot has permissions to send/read messages as well as connect to and speak in voice channels
    - Make sure you note down your bot's token
2. Go to the [Spotify Devloper Portal](https://developer.spotify.com/dashboard/) and create a new app.
    - Make sure you note down your Client ID and Client Secret
3. Create a `config.ini` file in the same format as the provided `example.ini` file in this project.
    - Make sure you update the sections with the tokens you noted for discord and spotify.
4. Install dependencies with `pip3 install -r requirements.txt`
5. Run the bot with `python3 mikey/mikey.py`

## Commands
```
Mikey's Magical Boombox

Music:
  connect     Connect to voice.
  now_playing Display information about the currently playing song.
  pause       Pause the currently playing song.
  play        Request a song and add it to the queue.
  queue       Retrieve a basic queue of upcoming songs.
  resume      Resume the currently paused song.
  shuffle     Shuffle the music in the queue
  skip        Skip the song.
  stop        Stop the currently playing song and destroy the player.
  trae        Reacts to one of Trae's jokes
  volume      Change the player volume.
​No Category:
  help        Shows this message

Type !help command for more info on a command.
You can also type !help category for more info on a category.
```

## Sources
- Based on this [example bot](https://gist.github.com/vbe0201/ade9b80f2d3b64643d854938d40a0a2d) by [vbe0201](https://github.com/vbe0201)
- Uses the [Discord.py API](https://discordpy.readthedocs.io/en/stable/api.html)
- Uses the [Spotipy API](https://spotipy.readthedocs.io/en/2.19.0/)
- Uses the [youtube-dl library](https://github.com/ytdl-org/youtube-dl)
