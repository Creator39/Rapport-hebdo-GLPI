from datetime import datetime
from zoneinfo import ZoneInfo

import pymysql

from rapport_glpi.__main__ import executer
from rapport_glpi.config import Settings
from rapport_glpi.discord import ErreurDiscord

MG = ZoneInfo("Indian/Antananarivo")
MAINTENANT = datetime(2026, 10, 19, 0, 5, tzinfo=MG)
URL = "https://discord.com/api/webhooks/1/abc"
SETTINGS = Settings(
    db_host="10.0.0.5",
    db_port=3306,
    db_name="db",
    db_user="rapport",
    db_password="secret",
    discord_webhook_url=URL,
)
LIGNES = [
    (1, 5, datetime(2026, 9, 28, 9, 0), datetime(2026, 9, 29, 9, 0), "Réseau", "srv-a"),
    (2, 2, datetime(2026, 9, 30, 9, 0), None, "Matériel", None),
]


class Curseur:
    def __init__(self, lignes):
        self.lignes = lignes
        self.params = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def execute(self, requete, params):
        self.params = params

    def fetchall(self):
        return self.lignes


class Connexion:
    def __init__(self, lignes):
        self.curseur = Curseur(lignes)
        self.fermee = False

    def cursor(self):
        return self.curseur

    def close(self):
        self.fermee = True


class Envoi:
    def __init__(self, erreur=None):
        self.appels = []
        self.erreur = erreur

    def __call__(self, morceaux, url):
        if self.erreur:
            raise self.erreur
        self.appels.append((list(morceaux), url))
        return len(morceaux)


def lancer(argv, envoi=None, connexion=None, configuration=SETTINGS):
    connexion = connexion or Connexion(LIGNES)
    envoi = envoi or Envoi()
    code = executer(
        argv,
        charger_configuration=lambda: configuration,
        connecter=lambda s: connexion,
        envoyer=envoi,
        maintenant=lambda: MAINTENANT,
    )
    return code, envoi, connexion


def test_dry_run_affiche_sans_envoyer(capsys):
    code, envoi, _ = lancer(["--dry-run"])

    sortie = capsys.readouterr().out
    assert code == 0
    assert envoi.appels == []
    assert "Rapport hebdomadaire GLPI" in sortie
    assert "Tickets créés : 2" in sortie
    assert "message 1/" in sortie


def test_envoi_reel_appelle_discord_avec_l_url(capsys):
    code, envoi, _ = lancer([])

    assert code == 0
    assert len(envoi.appels) == 1
    morceaux, url = envoi.appels[0]
    assert url == URL
    assert "Tickets créés : 2" in morceaux[0]
    assert "1 message(s) envoyé(s)." in capsys.readouterr().out


def test_fenetre_passee_a_la_requete_et_connexion_fermee():
    _, _, connexion = lancer(["--dry-run"])

    # Lundi 19/10 00:05 MG -> semaine du 12/10 au 18/10 (UTC naïf)
    from datetime import datetime as dt

    assert connexion.curseur.params == (dt(2026, 10, 11, 21, 0), dt(2026, 10, 18, 21, 0))
    assert connexion.fermee is True


def test_configuration_invalide_renvoie_1_sans_connexion(capsys):
    def configuration_cassee():
        raise ValueError("Variables manquantes dans .env : DB_PASSWORD")

    connexion = Connexion(LIGNES)
    code = executer(
        [],
        charger_configuration=configuration_cassee,
        connecter=lambda s: connexion,
        envoyer=Envoi(),
        maintenant=lambda: MAINTENANT,
    )

    assert code == 1
    assert "DB_PASSWORD" in capsys.readouterr().err
    assert connexion.curseur.params is None


def test_erreur_mysql_renvoie_1(capsys):
    class ConnexionEnPanne(Connexion):
        def cursor(self):
            raise pymysql.err.OperationalError(2003, "serveur injoignable")

    code, envoi, _ = lancer([], connexion=ConnexionEnPanne(LIGNES))

    assert code == 1
    assert envoi.appels == []
    assert "serveur injoignable" in capsys.readouterr().err


def test_erreur_discord_renvoie_1(capsys):
    code, _, _ = lancer([], envoi=Envoi(erreur=ErreurDiscord("Discord a répondu 500")))

    assert code == 1
    assert "Discord a répondu 500" in capsys.readouterr().err
