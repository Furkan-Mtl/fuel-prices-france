-- Échoue si un prix sort de la plage plausible (0,50 € à 4 €).
-- Ces prix doivent déjà être supprimés à la collecte (collecte.py).
select *
from {{ ref('stg_prix') }}
where prix < {{ var('prix_min') }} or prix > {{ var('prix_max') }}
