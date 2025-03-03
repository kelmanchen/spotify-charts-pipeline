WITH first_entry AS (
    SELECT 
        track_id
        , MIN(entry_date) AS first_entry_date
    FROM {{ ref('stg_chart_data') }}
    GROUP BY track_id
), 
monthly_counts AS (
    SELECT
        DATE_TRUNC('month', cd.entry_date) AS month_start
        , SUM(CASE WHEN cd.entry_date = fe.first_entry_date THEN 1 ELSE 0 END) AS new_entries_count
        , COUNT(DISTINCT cd.track_id) AS tracks_count
    FROM {{ ref('stg_chart_data') }} cd
        INNER JOIN first_entry fe
            ON cd.track_id = fe.track_id
    GROUP BY 1
)

SELECT 
    month_start
    , ROUND(100.0 * new_entries_count / tracks_count, 2) AS proportion_new_songs
FROM monthly_counts
ORDER BY month_start
OFFSET 1
