SELECT 
    a.artist_id
    , a.artist_name
    , COUNT(DISTINCT entry_date) AS num_days_in_top_10
FROM {{ ref('stg_chart_data') }} cd
    INNER JOIN {{ ref('stg_track_artists') }} ta
        ON cd.track_id = ta.track_id
    INNER JOIN {{ ref('stg_artists') }} a
        ON ta.artist_id = a.artist_id
WHERE cd.rank <= 10
GROUP BY 
    a.artist_id
    , a.artist_name
ORDER BY num_days_in_top_10 DESC
LIMIT 10
