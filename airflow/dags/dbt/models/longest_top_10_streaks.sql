WITH date_group AS (
    SELECT
        cd.track_id
        , cd.entry_date
        , DATEADD(DAY, -DENSE_RANK() OVER (PARTITION BY cd.track_id ORDER BY cd.entry_date), cd.entry_date) AS date_grp
    FROM {{ ref('stg_chart_data') }} cd
    WHERE cd.rank <= 10
),
consecutive_days AS (
    SELECT
        track_id
        , DATEDIFF(DAY, MIN(entry_date), MAX(entry_date)) AS num_days_consecutive
    FROM date_group
    GROUP BY 
        track_id
        , date_grp
)

SELECT 
    ta.track_id
    , ta.track_name
    , ta.artist_names
    , cd.num_days_consecutive
FROM consecutive_days cd
    INNER JOIN {{ ref('stg_track_artists_named') }} ta
        ON cd.track_id = ta.track_id
ORDER BY num_days_consecutive DESC
LIMIT 1
