"""
API REST des prix actuels des carburants.

Elle lit la vue v_prix_actuels de PostgreSQL (dernière collecte, prix à jour)
et expose trois points d'entrée en JSON.

Lancement :
    uvicorn api:app --reload --app-dir src

Documentation interactive : http://127.0.0.1:8000/docs
"""

from enum import Enum

from fastapi import FastAPI, HTTPException, Query
from psycopg.rows import dict_row

from chargement import connexion

app = FastAPI(
    title="API Prix des carburants en France",
    description="Prix actuels des stations, issus de la collecte quotidienne de l'API officielle.",
    version="1.0",
)


class Carburant(str, Enum):
    """Liste fermée des carburants : toute autre valeur renvoie une erreur 422."""

    gazole = "gazole"
    sp95 = "sp95"
    sp98 = "sp98"
    e10 = "e10"
    e85 = "e85"
    gplc = "gplc"


def requete(sql: str, parametres: tuple = ()) -> list[dict]:
    """Exécute une requête SELECT et renvoie les lignes sous forme de dictionnaires."""
    with connexion() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(sql, parametres)
            return cur.fetchall()


@app.get("/")
def accueil():
    """Vérifie que l'API fonctionne et indique la date de la dernière collecte."""
    lignes = requete("SELECT MAX(date_collecte) AS derniere_collecte FROM prix")
    return {"statut": "ok", "derniere_collecte": lignes[0]["derniere_collecte"]}


@app.get("/stations/{id_station}/prix")
def prix_station(id_station: int):
    """Prix actuels de tous les carburants vendus par une station."""
    lignes = requete(
        """
        SELECT carburant, prix, date_maj_prix, ville, adresse
        FROM v_prix_actuels
        WHERE id_station = %s
        ORDER BY carburant
        """,
        (id_station,),
    )
    if not lignes:
        raise HTTPException(status_code=404, detail="Station inconnue ou sans prix à jour")
    return {
        "id_station": id_station,
        "ville": lignes[0]["ville"],
        "adresse": lignes[0]["adresse"],
        "prix": [
            {"carburant": l["carburant"], "prix": l["prix"], "date_maj_prix": l["date_maj_prix"]}
            for l in lignes
        ],
    }


@app.get("/prix/moins-chers")
def stations_moins_cheres(
    carburant: Carburant,
    region: str | None = None,
    limite: int = Query(10, ge=1, le=100),
):
    """Stations les moins chères pour un carburant, en France ou dans une région."""
    sql = """
        SELECT id_station, ville, adresse, region, prix
        FROM v_prix_actuels
        WHERE carburant = %s
    """
    parametres = [carburant.value]
    if region:
        sql += " AND region = %s"
        parametres.append(region)
    sql += " ORDER BY prix, id_station LIMIT %s"
    parametres.append(limite)
    return requete(sql, tuple(parametres))


@app.get("/regions")
def mediane_par_region(carburant: Carburant):
    """Prix médian par région et écart à la médiane nationale, en centimes."""
    return requete(
        """
        WITH nationale AS (
            SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY prix) AS mediane
            FROM v_prix_actuels
            WHERE carburant = %s
        )
        SELECT v.region,
               COUNT(*) AS nb_stations,
               ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY v.prix)::numeric, 3) AS prix_median,
               ROUND(((PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY v.prix) - n.mediane) * 100)::numeric, 1)
                   AS ecart_centimes
        FROM v_prix_actuels v
        CROSS JOIN nationale n
        WHERE v.carburant = %s AND v.region IS NOT NULL
        GROUP BY v.region, n.mediane
        ORDER BY prix_median DESC
        """,
        (carburant.value, carburant.value),
    )
