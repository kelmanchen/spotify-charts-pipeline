WITH date_group AS (
    SELECT
        cd.track_id
        , t.track_name
        , cd.entry_date
        , DATEADD(DAY, -DENSE_RANK() OVER (PARTITION BY cd.track_id ORDER BY cd.entry_date), cd.entry_date) AS date_grp
    FROM {{ ref('stg_chart_data') }} cd
        LEFT JOIN {{ ref('stg_tracks') }} t
            ON cd.track_id = t.track_id
    WHERE cd.rank <= 50
),
consecutive_days AS (
    SELECT
        track_id
        , track_name
        , DATEDIFF(DAY, MIN(entry_date), MAX(entry_date)) AS num_days_consecutive
    FROM date_group
    GROUP BY 
        track_id
        , track_name
        , date_grp
),
consecutive_days_category AS (
    SELECT 
        *
        , CASE 
            WHEN num_days_consecutive <= 7 THEN '1 week'
            WHEN num_days_consecutive <= 3*7 THEN '2-3 weeks'
            WHEN num_days_consecutive <= 6*7 THEN '4-6 weeks'
            WHEN num_days_consecutive <= 9*7 THEN '7-9 weeks'
            WHEN num_days_consecutive <= 15*7 THEN '10-15 weeks'
            ELSE '16+ weeks'
        END AS consecutive_days_category
    FROM consecutive_days
    WHERE num_days_consecutive > 0
)

SELECT 
    consecutive_days_category
    , COUNT(*) AS num_tracks
FROM consecutive_days_category
GROUP BY consecutive_days_category
ORDER BY consecutive_days_category
