-- Prix typés, avec l'âge du prix au moment de la collecte
select
    id_station,
    lower(carburant)                                   as carburant,
    prix::numeric(5, 3)                                as prix,
    date_maj_prix,
    date_collecte,
    date_collecte::date                                as jour_collecte,
    date_maj_prix < date_collecte - interval '{{ var("jours_peremption") }} days'
                                                       as est_perime
from {{ source('brut', 'prix') }}
