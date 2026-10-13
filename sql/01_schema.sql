-- =========================================================
-- Schéma de la base « carburants »
-- A exécuter une seule fois, dans pgAdmin, sur la base carburants
-- =========================================================

-- Une ligne par station-service (informations descriptives)
CREATE TABLE IF NOT EXISTS stations (
    id_station        BIGINT PRIMARY KEY,
    adresse           TEXT,
    code_postal       VARCHAR(5),
    ville             TEXT,
    departement       TEXT,
    code_departement  VARCHAR(3),
    region            TEXT,
    code_region       VARCHAR(3),
    latitude          DOUBLE PRECISION,
    longitude         DOUBLE PRECISION,
    derniere_collecte TIMESTAMP
);

-- Une ligne par station, par carburant et par collecte (les faits)
CREATE TABLE IF NOT EXISTS prix (
    id_station     BIGINT       NOT NULL REFERENCES stations (id_station),
    carburant      VARCHAR(10)  NOT NULL,
    prix           NUMERIC(5,3) NOT NULL CHECK (prix > 0),
    date_maj_prix  TIMESTAMPTZ,
    date_collecte  TIMESTAMP    NOT NULL,
    PRIMARY KEY (id_station, carburant, date_collecte)
);

-- Index pour accélérer les analyses par date et par carburant
CREATE INDEX IF NOT EXISTS idx_prix_date_collecte ON prix (date_collecte);
CREATE INDEX IF NOT EXISTS idx_prix_carburant     ON prix (carburant);
