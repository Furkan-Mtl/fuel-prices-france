select *
from {{ ref('mart_qualite_collecte') }}
where part_prix_perimes < 0 or part_prix_perimes > 1
