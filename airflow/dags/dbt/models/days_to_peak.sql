WITH peak_rank_date AS (
    SELECT 
        track_id
        , MIN(entry_date) AS peak_date
    FROM {{ ref('stg_chart_data') }} cd
    WHERE rank = (SELECT MIN(rank) FROM {{ ref('stg_chart_data') }} cd2 WHERE cd2.track_id = cd.track_id)
    GROUP BY track_id
), 
first_entry AS (
    SELECT 
        track_id
        , MIN(entry_date) AS first_entry_date
    FROM {{ ref('stg_chart_data') }}
    GROUP BY track_id
),
days_to_peak AS (
    SELECT 
        fe.track_id
        , fe.first_entry_date
        , prd.peak_date
        , DATEDIFF(DAY, fe.first_entry_date, prd.peak_date) AS days_to_peak
    FROM first_entry fe
        INNER JOIN peak_rank_date prd
            ON fe.track_id = prd.track_id
)

SELECT 
    days_to_peak
    , COUNT(*) AS frequency
FROM days_to_peak
GROUP BY days_to_peak
ORDER BY days_to_peak
