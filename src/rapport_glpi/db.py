"""Accès MariaDB en lecture seule pour récupérer les tickets d'une fenêtre donnée."""

from dataclasses import dataclass
from datetime import datetime

# Valeurs standard du champ status de GLPI (à vérifier sur l'instance).
STATUTS_GLPI = {
    1: "Nouveau",
    2: "En cours",
    3: "En cours",  # Planifié : compté comme non terminé
    4: "En attente",
    5: "Résolu",
    6: "Clos",
}
STATUT_INCONNU = "Inconnu"

REQUETE_TICKETS = """
SELECT
    t.id,
    t.status,
    t.date_creation,
    t.solvedate,
    c.name AS categorie,
    (SELECT co.name
       FROM glpi_items_tickets it
       JOIN glpi_computers co ON co.id = it.items_id
      WHERE it.tickets_id = t.id AND it.itemtype = 'Computer'
      LIMIT 1) AS equipement
FROM glpi_tickets t
LEFT JOIN glpi_itilcategories c ON c.id = t.itilcategories_id
WHERE t.is_deleted = 0
  AND t.date_creation >= %s
  AND t.date_creation < %s
ORDER BY t.id
"""


@dataclass(frozen=True)
class Ticket:
    id: int
    statut: str
    date_creation: datetime
    date_resolution: datetime | None
    categorie: str | None
    equipement: str | None


def libelle_statut(code: int) -> str:
    return STATUTS_GLPI.get(code, STATUT_INCONNU)


def ligne_vers_ticket(ligne: tuple) -> Ticket:
    """Convertit une ligne de REQUETE_TICKETS en Ticket."""
    id_, status, date_creation, solvedate, categorie, equipement = ligne
    return Ticket(
        id=id_,
        statut=libelle_statut(status),
        date_creation=date_creation,
        date_resolution=solvedate,
        categorie=categorie,
        equipement=equipement,
    )


def recuperer_tickets(connexion, debut_utc: datetime, fin_utc: datetime) -> list[Ticket]:
    """Tickets créés dans [debut_utc, fin_utc[, en UTC naïf comme stocké par MariaDB.

    `connexion` est une connexion PyMySQL ouverte avec le compte en lecture seule.
    """
    debut = debut_utc.replace(tzinfo=None)
    fin = fin_utc.replace(tzinfo=None)
    with connexion.cursor() as curseur:
        curseur.execute(REQUETE_TICKETS, (debut, fin))
        return [ligne_vers_ticket(ligne) for ligne in curseur.fetchall()]
