WITH track_artists AS (
	SELECT 
		t.track_id
		, t.track_name
		, LISTAGG(a.artist_name, ', ') WITHIN GROUP (ORDER BY a.artist_name) AS artist_names
	FROM {{ source('raw', 'tracks') }} t
		INNER JOIN {{ source('raw', 'track_artists') }} ta
			ON t.track_id = ta.track_id
		INNER JOIN {{ source('raw', 'artists') }} a
			ON ta.artist_id = a.artist_id
	GROUP BY 
		t.track_id
		, t.track_name
),
cleaned_track_ids AS (
    SELECT 
		track_name
		, artist_names
		, MIN(track_id) AS track_id_cleaned
    FROM track_artists
    GROUP BY track_name, artist_names	
)

SELECT 
	ta.track_id
	, cti.track_id_cleaned
FROM track_artists ta
	INNER JOIN cleaned_track_ids cti
		ON ta.track_name = cti.track_name
			AND ta.artist_names = cti.artist_names