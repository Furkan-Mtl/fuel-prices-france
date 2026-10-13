-- =========================================================
-- Vue des prix « actuels » : base de toutes les analyses
-- =========================================================
-- Ne garde que les prix de la dernière collecte, et écarte ceux qui
-- n'ont pas été mis à jour depuis plus de 7 jours (même règle que les
-- sites qui publient les moyennes nationales).

CREATE OR REPLACE VIEW v_prix_actuels AS
WITH derniere AS (
    SELECT MAX(date_collecte) AS d FROM prix
)
SELECT p.id_station, p.carburant, p.prix, p.date_maj_prix,
       s.ville, s.adresse, s.departement, s.region
FROM prix p
JOIN stations s ON s.id_station = p.id_station
JOIN derniere   ON p.date_collecte = derniere.d
WHERE p.date_maj_prix >= derniere.d - INTERVAL '7 days';
