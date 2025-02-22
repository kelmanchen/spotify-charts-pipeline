SELECT
    tcm.track_id_cleaned AS track_id,
    cd.entry_date,
    cd.rank
FROM {{ source('staging', 'chart_data') }} cd
INNER JOIN {{ ref('track_id_cleaned_map') }} tcm
    ON cd.track_id = tcm.track_id
