import configparser

# Read from config file
configFile = "config.ini"

config = configparser.ConfigParser()
config.read(configFile)

DISCORD_API_TOKEN = config["DISCORD"]["BotApiToken"]
SPOTIFY_CLIENT_ID = config["SPOTIFY"]["ClientId"]
SPOTIFY_CLIENT_SECRET = config["SPOTIFY"]["ClientSecret"]
MESSAGE_TIMEOUT = int(config["MIKEY"]["MessageTimeout"])
RAPID_API_KEY = config["RAPIDAPI"]["ApiKey"]