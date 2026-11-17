# Image unique pour l'API et le pipeline (collecte, chargement, dbt)
FROM python:3.12-slim

# Pas de fichiers .pyc, et les logs s'affichent tout de suite
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dépendances d'abord : Docker garde cette étape en cache tant que
# requirements.txt ne change pas
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code du projet
COPY src/ src/
COPY dbt_carburants/ dbt_carburants/

# Par défaut, le conteneur lance l'API
EXPOSE 8000
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "src"]
