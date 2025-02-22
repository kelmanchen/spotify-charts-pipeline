SELECT DISTINCT
    tcm.track_id_cleaned AS track_id,
    ta.artist_id
FROM {{ source('staging', 'track_artists') }} ta
INNER JOIN {{ ref('track_id_cleaned_map') }} tcm
    ON ta.track_id = tcm.track_id
