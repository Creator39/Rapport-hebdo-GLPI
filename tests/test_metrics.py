from datetime import datetime, timedelta

from rapport_glpi.db import Ticket
from rapport_glpi.metrics import calculer_indicateurs


def t(
    id,
    statut="En cours",
    creation=datetime(2026, 9, 28, 9, 0),
    resolution=None,
    categorie="Réseau",
    equipement=None,
):
    return Ticket(id, statut, creation, resolution, categorie, equipement)


def resolu(id, jours, equipement=None, categorie="Réseau"):
    creation = datetime(2026, 9, 28, 9, 0)
    resolution = creation + timedelta(days=jours)
    return t(id, "Résolu", creation, resolution, categorie, equipement)


def test_aucun_ticket():
    ind = calculer_indicateurs([])

    assert ind.crees == 0
    assert ind.resolus == 0
    assert ind.encours == 0
    assert ind.mediane_jours is None
    assert ind.mttr_jours is None
    assert ind.ratio_resolus_encours is None
    assert ind.top_pannes == []


def test_comptage_par_statut():
    tickets = [
        resolu(1, 1),
        t(2, "Clos"),
        t(3, "En cours"),
        t(4, "En attente"),
    ]

    ind = calculer_indicateurs(tickets)

    assert ind.crees == 4
    assert ind.resolus == 1
    assert ind.clos == 1
    assert ind.encours == 2  # En cours + En attente, pas Clos


def test_clos_nest_pas_compte_comme_resolu():
    ind = calculer_indicateurs([t(1, "Clos", resolution=datetime(2026, 9, 29, 9, 0))])

    assert ind.resolus == 0
    assert ind.clos == 1
    assert ind.mttr_jours is None


def test_duree_en_jours_calendaires_dates_seules():
    # Créé le 1er à 23h, résolu le 2 à 01h : 1 jour calendaire, pas 2 heures
    ticket = t(
        1,
        "Résolu",
        creation=datetime(2026, 10, 1, 23, 0),
        resolution=datetime(2026, 10, 2, 1, 0),
    )

    ind = calculer_indicateurs([ticket])

    assert ind.mttr_jours == 1


def test_mediane_seulement_a_partir_de_5_resolus():
    quatre = [resolu(i, 2) for i in range(4)]
    cinq = [resolu(i, 2) for i in range(5)]

    assert calculer_indicateurs(quatre).mediane_jours is None
    assert calculer_indicateurs(cinq).mediane_jours == 2


def test_mttr_est_la_moyenne_des_durees_resolues():
    tickets = [resolu(1, 1), resolu(2, 3)]

    assert calculer_indicateurs(tickets).mttr_jours == 2


def test_ratio_resolus_sur_encours():
    tickets = [resolu(1, 1), resolu(2, 1), t(3, "En cours"), t(4, "En attente")]

    assert calculer_indicateurs(tickets).ratio_resolus_encours == 1.0


def test_ratio_sans_encours_est_none():
    assert calculer_indicateurs([resolu(1, 1)]).ratio_resolus_encours is None


def test_top_pannes_seuil_de_2_et_tri_decroissant():
    tickets = [
        t(1, equipement="srv-a"),
        t(2, equipement="srv-a"),
        t(3, equipement="srv-a"),
        t(4, equipement="srv-b"),
        t(5, equipement="srv-b"),
        t(6, equipement="srv-c"),  # une seule panne : exclu
    ]

    ind = calculer_indicateurs(tickets)

    assert ind.top_pannes == [("srv-a", 3), ("srv-b", 2)]


def test_categories_sans_valeur_regroupees():
    tickets = [
        t(1, categorie="Réseau"),
        t(2, categorie="Réseau"),
        t(3, categorie=None),
    ]

    ind = calculer_indicateurs(tickets)

    assert ind.categories == {"Réseau": 2, "Non catégorisé": 1}
