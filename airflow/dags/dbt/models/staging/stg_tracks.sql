SELECT DISTINCT
    tcm.track_id_cleaned AS track_id
    , t.track_name
FROM {{ source('raw', 'tracks') }} t
    INNER JOIN {{ ref('track_id_cleaned_map') }} tcm
        ON t.track_id = tcm.track_id
