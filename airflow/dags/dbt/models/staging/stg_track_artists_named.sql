SELECT 
    t.track_id
    , t.track_name
    , LISTAGG(a.artist_name, ', ') WITHIN GROUP (ORDER BY a.artist_name) AS artist_names
FROM {{ ref('stg_tracks') }} t
    INNER JOIN {{ ref('stg_track_artists') }} ta
        ON t.track_id = ta.track_id
    INNER JOIN {{ ref('stg_artists') }} a
        ON ta.artist_id = a.artist_id
GROUP BY 
    t.track_id
    , t.track_name
