-- Petit jeu de données fictif utilisé par la CI pour lancer dbt build.
-- 3 stations, 2 collectes, dont un prix périmé et une station sans région.
INSERT INTO stations (id_station, adresse, code_postal, ville, departement, code_departement, region, code_region, latitude, longitude, derniere_collecte) VALUES
    (1, '1 rue A', '60000', 'beauvais', 'Oise', '60', 'Hauts-de-France', '32', 49.43, 2.08, '2026-10-24 09:00'),
    (2, '2 rue B', '67000', 'Strasbourg', 'Bas-Rhin', '67', 'Grand Est', '44', 48.57, 7.75, '2026-10-24 09:00'),
    (3, '3 rue C', '20000', 'Ajaccio', 'Corse-du-Sud', '2A', NULL, NULL, 41.92, 8.74, '2026-10-24 09:00');

INSERT INTO prix (id_station, carburant, prix, date_maj_prix, date_collecte) VALUES
    (1, 'gazole', 1.799, '2026-10-22 08:00', '2026-10-23 09:00'),
    (2, 'gazole', 1.859, '2026-10-22 08:00', '2026-10-23 09:00'),
    (1, 'gazole', 1.789, '2026-10-24 07:00', '2026-10-24 09:00'),
    (1, 'e10',    1.749, '2026-10-24 07:00', '2026-10-24 09:00'),
    (2, 'gazole', 1.869, '2026-10-23 18:00', '2026-10-24 09:00'),
    (2, 'e10',    1.799, '2026-10-01 10:00', '2026-10-24 09:00'),
    (3, 'gazole', 1.999, '2026-10-24 06:00', '2026-10-24 09:00');
