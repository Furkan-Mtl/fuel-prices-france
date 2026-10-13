"""
Pipeline quotidien : collecte des prix, puis chargement dans PostgreSQL.
C'est ce script que lance la tâche planifiée Windows.

Utilisation :
    python src/pipeline.py
"""

import chargement
import collecte

if __name__ == "__main__":
    collecte.main()
    chargement.main()
