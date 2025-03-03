SELECT 
    *
FROM {{ source('raw', 'artists') }}
WHERE artist_name <> ''
