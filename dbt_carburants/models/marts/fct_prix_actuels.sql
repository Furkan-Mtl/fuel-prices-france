-- Prix actuels : dernière collecte uniquement, prix périmés exclus.
-- Même règle que la vue v_prix_actuels utilisée par l'API.
with derniere_collecte as (
    select max(date_collecte) as date_collecte
    from {{ ref('stg_prix') }}
)

select
    p.id_station,
    p.carburant,
    p.prix,
    p.date_maj_prix,
    p.date_collecte,
    s.ville,
    s.departement,
    s.region
from {{ ref('stg_prix') }} p
join derniere_collecte d on p.date_collecte = d.date_collecte
join {{ ref('stg_stations') }} s on s.id_station = p.id_station
where not p.est_perime
