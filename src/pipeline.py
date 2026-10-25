"""
Pipeline quotidien : collecte des prix, chargement dans PostgreSQL,
puis construction et tests des modèles dbt.
C'est ce script que lance la tâche planifiée Windows.

Utilisation :
    python src/pipeline.py
"""

import sys

from dbt.cli.main import dbtRunner
from dotenv import load_dotenv

import chargement
import collecte

DOSSIER_DBT = chargement.RACINE / "dbt_carburants"


def construire_dbt() -> bool:
    """Lance « dbt build » : construit les modèles puis exécute les tests."""
    # dbt lit les identifiants PostgreSQL dans les variables d'environnement
    load_dotenv(chargement.RACINE / ".env")
    resultat = dbtRunner().invoke(
        ["build", "--project-dir", str(DOSSIER_DBT), "--profiles-dir", str(DOSSIER_DBT)]
    )
    return resultat.success


if __name__ == "__main__":
    collecte.main()
    chargement.main()
    if not construire_dbt():
        print("dbt build a échoué : voir les tests en erreur ci-dessus.")
        sys.exit(1)
