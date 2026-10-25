-- Échoue si une station a plusieurs prix pour le même carburant
-- dans les prix actuels (doublon de collecte).
select id_station, carburant, count(*) as nb
from {{ ref('fct_prix_actuels') }}
group by id_station, carburant
having count(*) > 1
