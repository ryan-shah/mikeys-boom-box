import spotipy
from constants import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET


# set up spotify connection
def connectToSpotify():
    credentials = spotipy.oauth2.SpotifyClientCredentials(
        client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET
    )
    return spotipy.Spotify(client_credentials_manager=credentials)
