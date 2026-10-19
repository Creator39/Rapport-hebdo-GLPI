from datetime import datetime, timezone

from rapport_glpi.db import (
    REQUETE_TICKETS,
    STATUT_INCONNU,
    libelle_statut,
    ligne_vers_ticket,
    recuperer_tickets,
)


class FauxCurseur:
    def __init__(self, lignes):
        self.lignes = lignes
        self.executions = []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def execute(self, requete, parametres):
        self.executions.append((requete, parametres))

    def fetchall(self):
        return self.lignes


class FauxConnexion:
    def __init__(self, lignes):
        self.curseur = FauxCurseur(lignes)

    def cursor(self):
        return self.curseur


def test_libelles_des_statuts_glpi():
    assert libelle_statut(1) == "Nouveau"
    assert libelle_statut(2) == "En cours"
    assert libelle_statut(3) == "En cours"
    assert libelle_statut(4) == "En attente"
    assert libelle_statut(5) == "Résolu"
    assert libelle_statut(6) == "Clos"


def test_statut_inconnu_ne_plante_pas():
    assert libelle_statut(99) == STATUT_INCONNU


def test_ligne_convertie_en_ticket():
    ligne = (
        33,
        5,
        datetime(2026, 9, 28, 9, 0),
        datetime(2026, 9, 29, 10, 0),
        "Réseau",
        "srv-a",
    )

    ticket = ligne_vers_ticket(ligne)

    assert ticket.id == 33
    assert ticket.statut == "Résolu"
    assert ticket.date_resolution == datetime(2026, 9, 29, 10, 0)
    assert ticket.categorie == "Réseau"
    assert ticket.equipement == "srv-a"


def test_ticket_sans_resolution_ni_categorie_ni_equipement():
    ligne = (1, 1, datetime(2026, 9, 28, 9, 0), None, None, None)

    ticket = ligne_vers_ticket(ligne)

    assert ticket.statut == "Nouveau"
    assert ticket.date_resolution is None
    assert ticket.categorie is None
    assert ticket.equipement is None


def test_fenetre_passee_en_utc_naif_avec_parametres_lies():
    connexion = FauxConnexion([])
    debut = datetime(2026, 9, 27, 21, 0, tzinfo=timezone.utc)
    fin = datetime(2026, 10, 4, 21, 0, tzinfo=timezone.utc)

    recuperer_tickets(connexion, debut, fin)

    requete, parametres = connexion.curseur.executions[0]
    assert requete == REQUETE_TICKETS
    assert parametres == (datetime(2026, 9, 27, 21, 0), datetime(2026, 10, 4, 21, 0))


def test_requete_ne_compte_que_les_computers_et_pas_les_formulaires():
    # Les liens Glpi\Form\Form ne sont pas des équipements : ils sont exclus du top
    assert "it.itemtype = 'Computer'" in REQUETE_TICKETS
    assert "is_deleted = 0" in REQUETE_TICKETS


def test_recuperation_renvoie_des_tickets():
    lignes = [(2, 2, datetime(2026, 9, 28, 9, 0), None, "Réseau", None)]
    connexion = FauxConnexion(lignes)

    tickets = recuperer_tickets(
        connexion,
        datetime(2026, 9, 27, 21, 0, tzinfo=timezone.utc),
        datetime(2026, 10, 4, 21, 0, tzinfo=timezone.utc),
    )

    assert len(tickets) == 1
    assert tickets[0].statut == "En cours"
