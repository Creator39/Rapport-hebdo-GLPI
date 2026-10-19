"""Mise en forme du rapport et découpage du message pour Discord. Fonctions pures."""

from datetime import datetime, timedelta

from rapport_glpi.metrics import Indicateurs
from rapport_glpi.window import REPORT_TZ

LIMITE_DISCORD = 2000  # caractères maximum par message


def _format_jours(valeur: float | None) -> str:
    return "n/a" if valeur is None else f"{valeur:g} jour(s)"


def formater_rapport(ind: Indicateurs, debut_utc: datetime, fin_utc: datetime) -> str:
    """Construit le texte du rapport. `fin_utc` est exclue."""
    debut_local = debut_utc.astimezone(REPORT_TZ)
    dernier_jour = (fin_utc.astimezone(REPORT_TZ) - timedelta(days=1)).date()

    if ind.mediane_jours is None:
        mediane = "n/a (moins de 5 tickets résolus)"
    else:
        mediane = _format_jours(ind.mediane_jours)

    ratio = "n/a" if ind.ratio_resolus_encours is None else f"{ind.ratio_resolus_encours:.2f}"
    mttr = "n/a" if ind.mttr_jours is None else f"{ind.mttr_jours:.1f} jour(s)"

    lignes = [
        f"**Rapport hebdomadaire GLPI** — du {debut_local.strftime('%d/%m/%Y')} "
        f"au {dernier_jour.strftime('%d/%m/%Y')}",
        "",
        f"- Tickets créés : {ind.crees}",
        f"- Résolus : {ind.resolus}",
        f"- Clos : {ind.clos}",
        f"- En cours : {ind.encours}",
        f"- Ratio résolus / en cours : {ratio}",
        f"- Temps médian de résolution : {mediane}",
        f"- Temps moyen de résolution (MTTR) : {mttr}",
        "",
        "**Équipements les plus défaillants** (2 pannes ou plus)",
    ]

    if ind.top_pannes:
        lignes += [f"- {equip} : {n} pannes" for equip, n in ind.top_pannes]
    else:
        lignes.append("- Aucun")

    lignes += ["", "**Répartition par catégorie**"]
    if ind.categories:
        lignes += [f"- {cat} : {n}" for cat, n in sorted(ind.categories.items())]
    else:
        lignes.append("- Aucune")

    return "\n".join(lignes)


def decouper(message: str, limite: int = LIMITE_DISCORD) -> list[str]:
    """Découpe le message en morceaux de `limite` caractères maximum.

    Les coupures se font entre les lignes quand c'est possible. Une ligne plus
    longue que la limite est coupée en plein milieu.
    """
    if limite < 1:
        raise ValueError("limite doit être strictement positive")

    morceaux: list[str] = []
    courant = ""

    for ligne in message.split("\n"):
        while len(ligne) > limite:
            if courant:
                morceaux.append(courant)
                courant = ""
            morceaux.append(ligne[:limite])
            ligne = ligne[limite:]

        candidat = ligne if not courant else f"{courant}\n{ligne}"
        if len(candidat) <= limite:
            courant = candidat
        else:
            morceaux.append(courant)
            courant = ligne

    if courant or not morceaux:
        morceaux.append(courant)

    return morceaux
