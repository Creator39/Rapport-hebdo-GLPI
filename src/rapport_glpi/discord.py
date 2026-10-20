"""Envoi du rapport au webhook Discord."""

import time
from collections.abc import Iterable

import requests

TIMEOUT_SECONDES = 10
TENTATIVES_MAX = 3
ATTENTE_MAX_SECONDES = 60


class ErreurDiscord(RuntimeError):
    """Discord a refusé l'envoi ou n'a pas répondu."""


def envoyer_messages(
    morceaux: Iterable[str],
    webhook_url: str,
    session=None,
    pause=time.sleep,
) -> int:
    """Envoie chaque morceau dans l'ordre. Renvoie le nombre de messages envoyés.

    Les mentions sont désactivées (`allowed_mentions`) pour éviter de notifier
    tout le salon. En cas de limitation (429), attend le délai indiqué par Discord
    puis réessaie, jusqu'à TENTATIVES_MAX fois par message.
    """
    session = session or requests
    envoyes = 0

    for morceau in morceaux:
        _envoyer_un(morceau, webhook_url, session, pause)
        envoyes += 1

    return envoyes


def _envoyer_un(contenu: str, webhook_url: str, session, pause) -> None:
    charge = {"content": contenu, "allowed_mentions": {"parse": []}}

    for tentative in range(1, TENTATIVES_MAX + 1):
        try:
            reponse = session.post(webhook_url, json=charge, timeout=TIMEOUT_SECONDES)
        except requests.RequestException as erreur:
            raise ErreurDiscord(f"Connexion à Discord impossible : {erreur}") from erreur

        if reponse.status_code in (200, 204):
            return

        if reponse.status_code == 429 and tentative < TENTATIVES_MAX:
            attente = _delai_attente(reponse)
            pause(min(attente, ATTENTE_MAX_SECONDES))
            continue

        raise ErreurDiscord(
            f"Discord a répondu {reponse.status_code} (tentative {tentative})"
        )


def _delai_attente(reponse) -> float:
    try:
        return float(reponse.json().get("retry_after", 1))
    except (ValueError, AttributeError):
        return 1.0
