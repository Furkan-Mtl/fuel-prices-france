-- Suivi de la qualité : pour chaque jour de collecte et chaque carburant,
-- nombre de prix reçus et part des prix périmés
with derniere_par_jour as (
    -- S'il y a eu plusieurs collectes le même jour, on garde la dernière
    select jour_collecte, max(date_collecte) as date_collecte
    from {{ ref('stg_prix') }}
    group by jour_collecte
)

select
    p.jour_collecte,
    p.carburant,
    count(*)                                                  as nb_prix,
    count(*) filter (where p.est_perime)                      as nb_prix_perimes,
    round(avg(case when p.est_perime then 1 else 0 end), 3)   as part_prix_perimes
from {{ ref('stg_prix') }} p
join derniere_par_jour d on d.date_collecte = p.date_collecte
group by p.jour_collecte, p.carburant
