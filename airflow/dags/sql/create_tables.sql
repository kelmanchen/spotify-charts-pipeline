CREATE TABLE IF NOT EXISTS artists (
    artist_id VARCHAR(255) PRIMARY KEY
    , artist_name VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS tracks (
    track_id VARCHAR(255) PRIMARY KEY
    , track_name VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS track_artists (
    track_id VARCHAR(255)
    , artist_id VARCHAR(255)
    , PRIMARY KEY (track_id, artist_id)
    , FOREIGN KEY (track_id) REFERENCES tracks(track_id)
    , FOREIGN KEY (artist_id) REFERENCES artists(artist_id)    
);

CREATE TABLE IF NOT EXISTS chart_data (
    track_id VARCHAR(255)
    , entry_date DATE
    , rank INT
    , PRIMARY KEY (track_id, entry_date)
    , FOREIGN KEY (track_id) REFERENCES tracks(track_id)
);
