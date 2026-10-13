"""
Chargement des fichiers collectés (data/raw/*.csv) dans PostgreSQL.

- Les stations sont insérées, ou mises à jour si elles existent déjà.
- Les prix sont ajoutés ; une ligne déjà chargée est ignorée.
  Le script peut donc être relancé sans risque de créer des doublons.

Les paramètres de connexion sont lus dans le fichier .env (non versionné).

Utilisation :
    python src/chargement.py
"""

import os
from pathlib import Path

import pandas as pd
import psycopg
from dotenv import load_dotenv

RACINE = Path(__file__).resolve().parent.parent
DOSSIER_RAW = RACINE / "data" / "raw"

# Colonnes à lire comme du texte : sinon pandas transforme "01000" en 1000
COLONNES_TEXTE = {"cp": str, "code_departement": str, "code_region": str}

SQL_STATION = """
    INSERT INTO stations (id_station, adresse, code_postal, ville, departement,
                          code_departement, region, code_region,
                          latitude, longitude, derniere_collecte)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (id_station) DO UPDATE SET
        adresse           = EXCLUDED.adresse,
        code_postal       = EXCLUDED.code_postal,
        ville             = EXCLUDED.ville,
        departement       = EXCLUDED.departement,
        code_departement  = EXCLUDED.code_departement,
        region            = EXCLUDED.region,
        code_region       = EXCLUDED.code_region,
        latitude          = EXCLUDED.latitude,
        longitude         = EXCLUDED.longitude,
        derniere_collecte = EXCLUDED.derniere_collecte
    WHERE stations.derniere_collecte IS NULL
       OR EXCLUDED.derniere_collecte >= stations.derniere_collecte
"""

SQL_PRIX = """
    INSERT INTO prix (id_station, carburant, prix, date_maj_prix, date_collecte)
    VALUES (%s, %s, %s, %s, %s)
    ON CONFLICT (id_station, carburant, date_collecte) DO NOTHING
"""


def connexion() -> psycopg.Connection:
    """Ouvre la connexion avec les paramètres du fichier .env."""
    load_dotenv(RACINE / ".env")
    return psycopg.connect(
        host=os.getenv("PGHOST", "localhost"),
        port=os.getenv("PGPORT", "5432"),
        dbname=os.getenv("PGDATABASE", "carburants"),
        user=os.getenv("PGUSER", "postgres"),
        password=os.getenv("PGPASSWORD"),
    )


def lire_fichiers() -> pd.DataFrame:
    """Lit et empile tous les CSV collectés."""
    fichiers = sorted(DOSSIER_RAW.glob("prix_*.csv"))
    if not fichiers:
        raise FileNotFoundError(f"Aucun fichier dans {DOSSIER_RAW}")
    print(f"  Fichiers trouvés          : {len(fichiers)}")

    df = pd.concat(
        (pd.read_csv(f, dtype=COLONNES_TEXTE) for f in fichiers),
        ignore_index=True,
    )
    df["prix"] = pd.to_numeric(df["prix"], errors="coerce")
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    df["date_collecte"] = pd.to_datetime(df["date_collecte"])
    df["date_maj_prix"] = pd.to_datetime(df["date_maj_prix"], errors="coerce", utc=True)

    avant = len(df)
    df = df.dropna(subset=["id", "carburant", "prix"])
    print(f"  Lignes lues               : {avant} (dont {avant - len(df)} écartées)")
    return df


def sans_nan(valeur):
    """Convertit les valeurs manquantes de pandas en NULL pour PostgreSQL."""
    return None if pd.isna(valeur) else valeur


def charger(df: pd.DataFrame) -> None:
    # Pour chaque station, on garde les informations de la collecte la plus récente
    stations = (
        df.sort_values("date_collecte")
          .drop_duplicates(subset="id", keep="last")
    )
    lignes_stations = [
        (int(s.id), sans_nan(s.adresse), sans_nan(s.cp), sans_nan(s.ville),
         sans_nan(s.departement), sans_nan(s.code_departement),
         sans_nan(s.region), sans_nan(s.code_region),
         sans_nan(s.latitude), sans_nan(s.longitude),
         s.date_collecte.to_pydatetime())
        for s in stations.itertuples()
    ]
    lignes_prix = [
        (int(p.id), p.carburant, float(p.prix),
         None if pd.isna(p.date_maj_prix) else p.date_maj_prix.to_pydatetime(),
         p.date_collecte.to_pydatetime())
        for p in df.itertuples()
    ]

    with connexion() as conn, conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM prix")
        avant = cur.fetchone()[0]

        cur.executemany(SQL_STATION, lignes_stations)
        cur.executemany(SQL_PRIX, lignes_prix)

        cur.execute("SELECT COUNT(*) FROM stations")
        nb_stations = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM prix")
        apres = cur.fetchone()[0]

    print(f"  Stations en base          : {nb_stations}")
    print(f"  Prix ajoutés              : {apres - avant}")
    print(f"  Prix en base              : {apres}")


def main() -> None:
    print("Chargement dans PostgreSQL")
    df = lire_fichiers()
    charger(df)


if __name__ == "__main__":
    main()
