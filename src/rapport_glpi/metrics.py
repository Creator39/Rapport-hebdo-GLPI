"""Indicateurs du rapport hebdomadaire. Fonctions pures : aucune entrée/sortie."""

from collections import Counter
from dataclasses import dataclass, field
from statistics import fmean, median

from rapport_glpi.db import Ticket

STATUT_RESOLU = "Résolu"
STATUT_CLOS = "Clos"
SEUIL_MEDIANE = 5  # nombre minimum de tickets résolus pour calculer la médiane
SEUIL_PANNES = 2  # nombre minimum de pannes par équipement pour le top
CATEGORIE_INCONNUE = "Non catégorisé"


@dataclass(frozen=True)
class Indicateurs:
    crees: int
    resolus: int
    clos: int
    encours: int
    mediane_jours: float | None
    mttr_jours: float | None
    ratio_resolus_encours: float | None
    top_pannes: list[tuple[str, int]] = field(default_factory=list)
    categories: dict[str, int] = field(default_factory=dict)


def duree_resolution_jours(ticket: Ticket) -> int | None:
    """Durée en jours calendaires entre date de création et date de résolution (dates seules)."""
    if ticket.date_resolution is None:
        return None
    return (ticket.date_resolution.date() - ticket.date_creation.date()).days


def calculer_indicateurs(tickets: list[Ticket]) -> Indicateurs:
    resolus = [t for t in tickets if t.statut == STATUT_RESOLU]
    clos = [t for t in tickets if t.statut == STATUT_CLOS]
    # En cours = tout ce qui n'est ni résolu ni clos (dont « En attente »)
    encours = [t for t in tickets if t.statut not in (STATUT_RESOLU, STATUT_CLOS)]

    durees = [d for t in resolus if (d := duree_resolution_jours(t)) is not None]
    mediane = median(durees) if len(durees) >= SEUIL_MEDIANE else None
    mttr = fmean(durees) if durees else None

    ratio = len(resolus) / len(encours) if encours else None

    pannes = Counter(t.equipement for t in tickets if t.equipement)
    top = sorted(
        ((equip, n) for equip, n in pannes.items() if n >= SEUIL_PANNES),
        key=lambda item: (-item[1], item[0]),
    )

    categories = Counter(t.categorie or CATEGORIE_INCONNUE for t in tickets)

    return Indicateurs(
        crees=len(tickets),
        resolus=len(resolus),
        clos=len(clos),
        encours=len(encours),
        mediane_jours=mediane,
        mttr_jours=mttr,
        ratio_resolus_encours=ratio,
        top_pannes=top,
        categories=dict(categories),
    )
