-- Stations nettoyées : textes sans espaces superflus, région absente explicite
select
    id_station,
    trim(adresse)                         as adresse,
    code_postal,
    initcap(trim(ville))                  as ville,
    departement,
    code_departement,
    nullif(trim(region), '')              as region,
    latitude,
    longitude
from {{ source('brut', 'stations') }}
