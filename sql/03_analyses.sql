-- =========================================================
-- Analyses des prix des carburants (dernière collecte)
-- Toutes les requêtes s'appuient sur la vue v_prix_actuels
-- =========================================================


-- ---------------------------------------------------------
-- 1. Prix moyen et prix médian par carburant
-- ---------------------------------------------------------
-- La médiane résiste mieux que la moyenne aux stations très chères
-- (autoroutes) ou très bon marché (grandes surfaces).
-- PERCENTILE_CONT renvoie un nombre à virgule flottante : il faut le
-- convertir en numeric pour pouvoir l'arrondir avec ROUND(x, 3).
SELECT
    carburant,
    COUNT(*)                     AS nb_stations,
    ROUND(AVG(prix), 3)          AS prix_moyen,
    ROUND((PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY prix))::numeric, 3)
                                 AS prix_median
FROM v_prix_actuels
GROUP BY carburant
ORDER BY nb_stations DESC;


-- ---------------------------------------------------------
-- 2. Prix moyen du gazole par région, du plus cher au moins cher
-- ---------------------------------------------------------
SELECT
    region,
    COUNT(*)            AS nb_stations,
    ROUND(AVG(prix), 3) AS prix_moyen_gazole
FROM v_prix_actuels
WHERE carburant = 'gazole'
  AND region IS NOT NULL
GROUP BY region
ORDER BY prix_moyen_gazole DESC;


-- ---------------------------------------------------------
-- 3. Les 10 stations les moins chères en gazole dans les Hauts-de-France
-- ---------------------------------------------------------
SELECT ville, adresse, prix
FROM v_prix_actuels
WHERE carburant = 'gazole'
  AND region = 'Hauts-de-France'
ORDER BY prix
LIMIT 10;


-- ---------------------------------------------------------
-- 4. Pour chaque carburant : écart entre la région la plus chère
--    et la région la moins chère
-- ---------------------------------------------------------
-- Étape 1 (CTE) : prix moyen par carburant et par région.
-- Étape 2 : pour chaque carburant, on compare la plus forte et la plus
-- faible de ces moyennes. ARRAY_AGG(... ORDER BY ...)[1] récupère le nom
-- de la région correspondante.
WITH moyennes AS (
    SELECT carburant, region, AVG(prix) AS prix_moyen
    FROM v_prix_actuels
    WHERE region IS NOT NULL
    GROUP BY carburant, region
)
SELECT
    carburant,
    (ARRAY_AGG(region ORDER BY prix_moyen DESC))[1] AS region_la_plus_chere,
    ROUND(MAX(prix_moyen), 3)                       AS prix_max,
    (ARRAY_AGG(region ORDER BY prix_moyen ASC))[1]  AS region_la_moins_chere,
    ROUND(MIN(prix_moyen), 3)                       AS prix_min,
    ROUND(MAX(prix_moyen) - MIN(prix_moyen), 3)     AS ecart
FROM moyennes
GROUP BY carburant
ORDER BY ecart DESC;


-- ---------------------------------------------------------
-- 5. Dans chaque région, la station la moins chère en gazole
-- ---------------------------------------------------------
-- ROW_NUMBER numérote les stations de chaque région (PARTITION BY region)
-- de la moins chère à la plus chère (ORDER BY prix).
-- On garde ensuite uniquement le numéro 1.
-- En cas d'égalité de prix, ROW_NUMBER n'en garde qu'une ;
-- RANK() les garderait toutes.
WITH classement AS (
    SELECT
        region, ville, adresse, prix,
        ROW_NUMBER() OVER (PARTITION BY region ORDER BY prix) AS rang
    FROM v_prix_actuels
    WHERE carburant = 'gazole'
      AND region IS NOT NULL
)
SELECT region, ville, adresse, prix
FROM classement
WHERE rang = 1
ORDER BY prix;


-- ---------------------------------------------------------
-- 6. Qualité des données : part des prix « périmés » par carburant
-- ---------------------------------------------------------
-- Pour la dernière collecte, quelle part des prix n'a pas été mise à jour
-- depuis plus de 7 jours ? Requête sur la table prix (et non sur la vue,
-- qui les a déjà retirés).
WITH derniere AS (
    SELECT MAX(date_collecte) AS d FROM prix
)
SELECT
    p.carburant,
    COUNT(*) AS nb_prix,
    COUNT(*) FILTER (WHERE p.date_maj_prix < derniere.d - INTERVAL '7 days')
             AS nb_perimes,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE p.date_maj_prix < derniere.d - INTERVAL '7 days')
        / COUNT(*), 1
    ) AS pct_perimes
FROM prix p
JOIN derniere ON p.date_collecte = derniere.d
GROUP BY p.carburant
ORDER BY pct_perimes DESC;
