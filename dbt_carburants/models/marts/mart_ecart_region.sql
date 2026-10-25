-- Prix médian par région et par carburant, et écart à la médiane nationale
with nationale as (
    select
        carburant,
        percentile_cont(0.5) within group (order by prix) as mediane_nationale
    from {{ ref('fct_prix_actuels') }}
    group by carburant
),

regionale as (
    select
        region,
        carburant,
        count(*)                                           as nb_stations,
        percentile_cont(0.5) within group (order by prix) as mediane_region
    from {{ ref('fct_prix_actuels') }}
    where region is not null
    group by region, carburant
)

select
    r.region,
    r.carburant,
    r.nb_stations,
    round(r.mediane_region::numeric, 3)                                     as prix_median,
    round(n.mediane_nationale::numeric, 3)                                  as prix_median_national,
    {{ en_centimes('(r.mediane_region - n.mediane_nationale)::numeric') }}  as ecart_centimes
from regionale r
join nationale n on n.carburant = r.carburant
