-- Échoue si le modèle dbt et la vue v_prix_actuels (utilisée par l'API)
-- ne renvoient pas le même nombre de prix actuels.
select dbt.nb as nb_dbt, vue.nb as nb_vue
from (select count(*) as nb from {{ ref('fct_prix_actuels') }}) dbt
cross join (select count(*) as nb from public.v_prix_actuels) vue
where dbt.nb <> vue.nb
