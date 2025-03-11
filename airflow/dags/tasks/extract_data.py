import requests
import datetime as dt
import pandas as pd
import logging

logging.basicConfig(
    filename="chart_scraper_log.log",
    level=logging.INFO
)

def get_chart_data(token, date_str):
    headers = {
        'Authorization': f'Bearer {token}',
    }
    url = f"https://charts-spotify-com-service.spotify.com/auth/v0/charts/regional-global-daily/{date_str}"

    # fetch charts data
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

    # iterate over every entri and populate
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

        # chart data
        chart_data.append({
            'track_id': track_id,
            'entry_date': date_str,
            'rank': entry['currentRank']
        })

    return tracks, artists, track_artists, chart_data

def get_all_chart_data(token, start_date, end_date, csv_url):
    current_date = start_date
    all_tracks, all_artists, all_track_artists, all_chart_data = [], [], [], []

    # fetch data for each date between start_date and end_date
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

    # preprocess each dataframe
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

    # output dataframes to csv
    for df, filename in df_list:
        df.to_csv(f'{csv_url}{filename}', index=False)
        logging.info(f"Saved {csv_url}{filename} with {len(df)} records.")

