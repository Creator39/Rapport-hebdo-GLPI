import pytest
import requests

from rapport_glpi.discord import ErreurDiscord, envoyer_messages

WEBHOOK = "https://discord.com/api/webhooks/123/abc"


class Reponse:
    def __init__(self, status, json_data=None):
        self.status_code = status
        self._json = json_data

    def json(self):
        if self._json is None:
            raise ValueError("pas de JSON")
        return self._json


class FauxSession:
    def __init__(self, reponses):
        self.reponses = list(reponses)
        self.appels = []

    def post(self, url, json, timeout):
        self.appels.append({"url": url, "json": json, "timeout": timeout})
        suivante = self.reponses.pop(0)
        if isinstance(suivante, Exception):
            raise suivante
        return suivante


def pas_de_pause(_secondes):
    return None


def test_envoi_de_plusieurs_morceaux_dans_l_ordre():
    session = FauxSession([Reponse(204), Reponse(204)])

    nombre = envoyer_messages(["premier", "second"], WEBHOOK, session, pas_de_pause)

    assert nombre == 2
    assert [a["json"]["content"] for a in session.appels] == ["premier", "second"]


def test_mentions_desactivees_et_timeout():
    session = FauxSession([Reponse(204)])

    envoyer_messages(["bonjour"], WEBHOOK, session, pas_de_pause)

    appel = session.appels[0]
    assert appel["json"]["allowed_mentions"] == {"parse": []}
    assert appel["timeout"] == 10
    assert appel["url"] == WEBHOOK


def test_limitation_429_puis_reussite():
    session = FauxSession([Reponse(429, {"retry_after": 2.5}), Reponse(204)])
    attentes = []

    nombre = envoyer_messages(["x"], WEBHOOK, session, attentes.append)

    assert nombre == 1
    assert attentes == [2.5]
    assert len(session.appels) == 2


def test_attente_plafonnee():
    session = FauxSession([Reponse(429, {"retry_after": 9999}), Reponse(204)])
    attentes = []

    envoyer_messages(["x"], WEBHOOK, session, attentes.append)

    assert attentes == [60]


def test_429_sans_json_attend_une_seconde():
    session = FauxSession([Reponse(429), Reponse(204)])
    attentes = []

    envoyer_messages(["x"], WEBHOOK, session, attentes.append)

    assert attentes == [1.0]


def test_erreur_http_leve_une_erreur_explicite():
    session = FauxSession([Reponse(404)])

    with pytest.raises(ErreurDiscord, match="404"):
        envoyer_messages(["x"], WEBHOOK, session, pas_de_pause)


def test_trop_de_429_abandonne():
    session = FauxSession([Reponse(429, {"retry_after": 1})] * 3)

    with pytest.raises(ErreurDiscord, match="429"):
        envoyer_messages(["x"], WEBHOOK, session, pas_de_pause)


def test_erreur_reseau_convertie():
    session = FauxSession([requests.ConnectionError("réseau coupé")])

    with pytest.raises(ErreurDiscord, match="Connexion"):
        envoyer_messages(["x"], WEBHOOK, session, pas_de_pause)


def test_aucun_morceau_aucun_appel():
    session = FauxSession([])

    assert envoyer_messages([], WEBHOOK, session, pas_de_pause) == 0
    assert session.appels == []
