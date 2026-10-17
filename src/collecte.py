"""
Collecte des prix des carburants en France.

Source : API officielle data.economie.gouv.fr
Jeu de données : « Prix des carburants en France - Flux instantané - v2 »
(mis à jour toutes les 10 minutes).

Le script télécharge toutes les stations, transforme les données au format
« une ligne = une station x un carburant », contrôle leur qualité, puis les
enregistre dans data/raw/ sous forme de fichier CSV daté.

Utilisation (depuis le dossier du projet, avec le .venv activé) :
    python src/collecte.py
"""

from datetime import datetime
from pathlib import Path

import pandas as pd
import requests

URL_EXPORT = (
    "https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/"
    "prix-des-carburants-en-france-flux-instantane-v2/exports/json"
)

CARBURANTS = ["gazole", "sp95", "sp98", "e10", "e85", "gplc"]

COLONNES_STATION = [
    "id", "adresse", "cp", "ville",
    "departement", "code_departement", "region", "code_region",
    "latitude", "longitude",
]

DOSSIER_SORTIE = Path(__file__).resolve().parent.parent / "data" / "raw"


def telecharger_stations() -> list[dict]:
    """Télécharge toutes les stations en un seul appel à l'API."""
    reponse = requests.get(URL_EXPORT, timeout=120)
    reponse.raise_for_status()
    return reponse.json()


def mettre_en_forme(stations: list[dict], date_collecte: datetime) -> pd.DataFrame:
    """
    Passe d'un format « large » (une colonne de prix par carburant)
    à un format « long » : une ligne par station et par carburant.
    Ce format est bien plus simple à analyser en SQL et dans Power BI.
    """
    lignes = []
    for station in stations:
        for carburant in CARBURANTS:
            prix = station.get(f"{carburant}_prix")
            if prix is None:
                # La station ne vend pas ce carburant : on ne crée pas de ligne.
                continue
            ligne = {colonne: station.get(colonne) for colonne in COLONNES_STATION}
            ligne["carburant"] = carburant
            ligne["prix"] = prix
            ligne["date_maj_prix"] = station.get(f"{carburant}_maj")
            ligne["date_collecte"] = date_collecte
            lignes.append(ligne)
    return pd.DataFrame(lignes)


def controler_qualite(df: pd.DataFrame) -> pd.DataFrame:
    """
    Contrôle la qualité des données et renvoie une copie nettoyée :
    - arrêt si aucune donnée n'a été récupérée ;
    - suppression des prix non numériques ou hors de [0,50 € ; 4 €] ;
    - suppression des doublons station / carburant.
    """
    if df.empty:
        raise ValueError("Aucune donnée récupérée : l'API a peut-être changé.")

    df = df.copy()
    df["prix"] = pd.to_numeric(df["prix"], errors="coerce")
    invalides = df["prix"].isna()
    aberrants = (df["prix"] < 0.5) | (df["prix"] > 4)
    doublons = df.duplicated(subset=["id", "carburant"])

    print(f"  Prix non numériques       : {invalides.sum()}")
    print(f"  Prix hors [0,50 € ; 4 €]  : {aberrants.sum()}")
    print(f"  Doublons station/carburant: {doublons.sum()}")

    propre = df[~invalides & ~aberrants].drop_duplicates(subset=["id", "carburant"])
    print(f"  Lignes conservées         : {len(propre)} / {len(df)}")
    return propre


def main() -> None:
    date_collecte = datetime.now().replace(microsecond=0)
    print(f"Collecte du {date_collecte:%d/%m/%Y à %H:%M}")

    stations = telecharger_stations()
    print(f"  Stations téléchargées     : {len(stations)}")

    df = mettre_en_forme(stations, date_collecte)
    print(f"  Lignes station x carburant: {len(df)}")

    df = controler_qualite(df)

    DOSSIER_SORTIE.mkdir(parents=True, exist_ok=True)
    fichier = DOSSIER_SORTIE / f"prix_{date_collecte:%Y-%m-%d_%Hh%M}.csv"
    df.to_csv(fichier, index=False, encoding="utf-8")
    print(f"  Fichier enregistré        : {fichier}")


if __name__ == "__main__":
    main()
