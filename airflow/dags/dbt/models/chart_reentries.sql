WITH chart_reentries AS (
    SELECT 
        *
        , DATEDIFF(DAY, LAG(entry_date) OVER (PARTITION BY track_id ORDER BY entry_date), entry_date) AS days_since_last_entry
    FROM {{ ref('stg_chart_data') }}
)

SELECT 
    ta.track_id
    , ta.track_name
    , ta.artist_names
    , COUNT(entry_date) AS number_reentries
    , MAX(rank) AS peak_rank
FROM chart_reentries cr
    LEFT JOIN {{ ref('stg_track_artists_named') }} ta
        ON cr.track_id = ta.track_id
WHERE days_since_last_entry > 7
GROUP BY ta.track_id, ta.track_name, ta.artist_names
ORDER BY number_reentries DESC
LIMIT 10
