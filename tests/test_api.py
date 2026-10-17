"""Tests de validation de l'API : ils ne nécessitent pas de base de données."""

from fastapi.testclient import TestClient

from api import app

client = TestClient(app)


def test_carburant_inconnu_renvoie_422():
    reponse = client.get("/regions", params={"carburant": "diesel"})
    assert reponse.status_code == 422


def test_limite_hors_bornes_renvoie_422():
    reponse = client.get("/prix/moins-chers", params={"carburant": "gazole", "limite": 0})
    assert reponse.status_code == 422
