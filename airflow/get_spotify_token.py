import spotipy
import os

from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv, set_key

load_dotenv()

def get_spotify_token():
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=os.getenv('CLIENT_ID'),
        client_secret=os.getenv('CLIENT_SECRET'),
        redirect_uri=os.getenv('REDIRECT_URI'),
        scope='user-read-private'
    ))
    token = sp.auth_manager.get_access_token(as_dict=False, check_cache=False)

    set_key("airflow/.env", "SPOTIFY_ACCESS_TOKEN", token)

    print(f"Access Token: {token}")

if __name__ == "__main__":
    get_spotify_token()
    