import spotipy
import os
import requests
import datetime as dt
import pandas as pd
import logging

from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

# Configure Logging
logging.basicConfig(
    filename="chart_scraper_log.log",
    level=logging.INFO,
)

load_dotenv()

def get_spotify_token():
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=os.getenv('CLIENT_ID'),
        client_secret=os.getenv('CLIENT_SECRET'),
        redirect_uri=os.getenv('REDIRECT_URI'),
        scope='user-read-private'
    ))
    token = sp.auth_manager.get_access_token(as_dict=False)

    return token

def get_chart_data(token, date_str):
    headers = {
        'Authorization': f'Bearer {token}',
    }
    url = f"https://charts-spotify-com-service.spotify.com/auth/v0/charts/regional-global-daily/{date_str}"

    try:
        r = requests.get(url=url, headers=headers)
        r.raise_for_status()
        logging.info(f"Successfully fetched data for {date_str}.")
        return r.json()['entries']
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch data for {date_str}: {e}")
        raise SystemExit(e)

def process_entries(entries, date_str):
    tracks = []
    artists = []
    track_artists = []
    chart_data = [] 

    for entry in entries:
        meta = entry['trackMetadata']
        entry = entry['chartEntryData']

        track_id = meta['trackUri'].split(":")[-1]

        # tracks
        tracks.append({
            'track_id': track_id,
            'track_name': meta['trackName'],
        })

        for artist in meta['artists']:
            artist_id = artist['spotifyUri'].split(":")[-1]

            # artists
            artists.append({
                'artist_id': artist_id,
                'artist_name': artist['name']
            })

            # track artists
            track_artists.append({
                'track_id': track_id,
                'artist_id': artist_id
            })

        chart_data.append({
            'track_id': track_id,
            'rank': entry['currentRank'],
            'entry_date': date_str
        })

    return tracks, artists, track_artists, chart_data

def get_all_chart_data(token, start_date, end_date):
    current_date = start_date

    all_tracks = []
    all_artists = []
    all_track_artists = []
    all_chart_data = []

    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        logging.info(f"Fetching data for {date_str}...")
        entries = get_chart_data(token, date_str)

        if entries:
            tracks, artists, track_artists, chart_data = process_entries(entries, date_str)
            all_tracks.extend(tracks)
            all_artists.extend(artists)
            all_track_artists.extend(track_artists)
            all_chart_data.extend(chart_data)
        else:
            logging.warning(f"No data found for {date_str}.")

        current_date += dt.timedelta(days=1)

    tracks_df = pd.DataFrame(all_tracks).drop_duplicates()
    artists_df = pd.DataFrame(all_artists).drop_duplicates()
    track_artists_df = pd.DataFrame(all_track_artists).drop_duplicates()
    chart_data_df = pd.DataFrame(all_chart_data)

    df_list = [
        (tracks_df, "tracks.csv"),
        (artists_df, "artists.csv"),
        (track_artists_df, "track_artists.csv"),
        (chart_data_df, "chart_data.csv"),
    ]

    for df, filename in df_list:
        df.to_csv(filename, index=False)
        logging.info(f"Saved {filename} with {len(df)} records.")


if __name__ == "__main__":
    START_DATE = dt.datetime(2024, 1, 1)
    END_DATE = dt.datetime(2024, 6, 30)
    token = get_spotify_token()
    get_all_chart_data(token, START_DATE, END_DATE)

