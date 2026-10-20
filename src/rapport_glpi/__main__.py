"""Point d'entrée : python -m rapport_glpi [--dry-run]

Enchaîne : configuration -> fenêtre -> tickets -> indicateurs -> rapport -> Discord.
"""

import argparse
import sys
from collections.abc import Callable, Mapping
from datetime import datetime, timezone
from pathlib import Path

import pymysql

from rapport_glpi.config import Settings, lire_fichier_env
from rapport_glpi.db import recuperer_tickets
from rapport_glpi.discord import ErreurDiscord, envoyer_messages
from rapport_glpi.metrics import calculer_indicateurs
from rapport_glpi.report import decouper, formater_rapport
from rapport_glpi.window import previous_week_window

FICHIER_ENV = Path(".env")


def lire_configuration(
    chemin: Path = FICHIER_ENV, environnement: Mapping[str, str] | None = None
) -> Settings:
    """Lit le .env s'il existe, sinon les variables d'environnement."""
    if chemin.exists():
        env = lire_fichier_env(chemin)
    else:
        import os

        env = dict(environnement if environnement is not None else os.environ)
    return Settings.depuis_variables(env)


def ouvrir_connexion(configuration: Settings):
    """Connexion MariaDB en lecture seule (le compte n'a que SELECT)."""
    return pymysql.connect(
        host=configuration.db_host,
        port=configuration.db_port,
        user=configuration.db_user,
        password=configuration.db_password,
        database=configuration.db_name,
        charset="utf8mb4",
        connect_timeout=10,
        read_timeout=30,
    )


def executer(
    argv: list[str],
    charger_configuration: Callable[[], Settings],
    connecter: Callable[[Settings], object],
    envoyer: Callable[[list[str], str], int],
    maintenant: Callable[[], datetime],
) -> int:
    """Exécute le rapport. Renvoie le code de sortie (0 = succès, 1 = erreur)."""
    parser = argparse.ArgumentParser(description="Rapport hebdomadaire GLPI vers Discord")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="affiche le rapport dans le terminal sans rien envoyer à Discord",
    )
    args = parser.parse_args(argv)

    try:
        configuration = charger_configuration()
        debut, fin = previous_week_window(maintenant())

        connexion = connecter(configuration)
        try:
            tickets = recuperer_tickets(connexion, debut, fin)
        finally:
            connexion.close()

        indicateurs = calculer_indicateurs(tickets)
        morceaux = decouper(formater_rapport(indicateurs, debut, fin))
    except (ValueError, pymysql.MySQLError) as erreur:
        print(f"Erreur : {erreur}", file=sys.stderr)
        return 1

    if args.dry_run:
        for numero, morceau in enumerate(morceaux, start=1):
            print(f"--- message {numero}/{len(morceaux)} ---")
            print(morceau)
        return 0

    try:
        nombre = envoyer(morceaux, configuration.discord_webhook_url)
    except ErreurDiscord as erreur:
        print(f"Erreur Discord : {erreur}", file=sys.stderr)
        return 1

    print(f"{nombre} message(s) envoyé(s).")
    return 0


def main(argv: list[str] | None = None) -> int:
    return executer(
        sys.argv[1:] if argv is None else argv,
        charger_configuration=lire_configuration,
        connecter=ouvrir_connexion,
        envoyer=envoyer_messages,
        maintenant=lambda: datetime.now(timezone.utc),
    )


if __name__ == "__main__":
    sys.exit(main())
