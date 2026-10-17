"""Tests de la mise en forme et du contrôle qualité (sans appel à l'API)."""

from datetime import datetime

import pandas as pd
import pytest

from collecte import controler_qualite, mettre_en_forme

DATE = datetime(2026, 10, 17, 9, 0)


def test_mettre_en_forme_une_ligne_par_carburant_vendu():
    stations = [{"id": 1, "ville": "Beauvais", "gazole_prix": 2.30, "sp95_prix": 2.20}]
    df = mettre_en_forme(stations, DATE)
    assert len(df) == 2  # la station ne vend que 2 carburants sur 6
    assert set(df["carburant"]) == {"gazole", "sp95"}
    assert (df["date_collecte"] == DATE).all()


def test_controler_qualite_retire_les_prix_invalides_et_aberrants():
    df = pd.DataFrame({
        "id": [1, 2, 3, 4],
        "carburant": ["gazole"] * 4,
        "prix": [2.0, 0.1, 5.0, "abc"],
    })
    propre = controler_qualite(df)
    assert list(propre["id"]) == [1]


def test_controler_qualite_retire_les_doublons():
    df = pd.DataFrame({"id": [1, 1], "carburant": ["gazole", "gazole"], "prix": [2.0, 2.0]})
    assert len(controler_qualite(df)) == 1


def test_controler_qualite_arrete_si_aucune_donnee():
    with pytest.raises(ValueError):
        controler_qualite(pd.DataFrame())
