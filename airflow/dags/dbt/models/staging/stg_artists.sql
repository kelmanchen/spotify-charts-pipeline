{{ config(materialized='view') }}

SELECT *
FROM {{ source('staging', 'artists') }}
WHERE artist_name <> ''
