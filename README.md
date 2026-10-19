# Rapport hebdomadaire GLPI

Génère chaque semaine un rapport d'incidents à partir des tickets GLPI créés pendant la semaine passée, puis l'envoie sur Discord.

## Fonctionnement

- Exécution via cron sur l'hôte, le dimanche à 21:05 UTC (lundi 00:00 à Madagascar, UTC+3).
- Fenêtre : tickets créés du lundi 00:00 (heure de Madagascar) au lundi suivant 00:00 exclu.
- Lecture SQL directe sur MariaDB, avec un compte en lecture seule dédié.
- Envoi sur un canal Discord réservé aux administrateurs (le rapport contient des adresses IP).

Le détail des règles métier est dans [docs/specification.md](docs/specification.md).

## Installation

Le projet utilise [uv](https://docs.astral.sh/uv/).

```bash
uv sync                # crée .venv et installe les dépendances (dont le groupe dev)
cp .env_example .env   # puis renseigner les valeurs locales
```

## Lancer

```bash
uv run python -m src.main
```

## Tests

Les tests tournent sur des données contrôlées, jamais sur une copie de la production.

```bash
uv run pytest
```

## Ajouter une dépendance

```bash
uv add <paquet>            # dépendance d'exécution
uv add --dev <paquet>      # dépendance de test
```

Committer `pyproject.toml` et `uv.lock`.

## Sécurité

- Aucun secret dans le dépôt : mots de passe, tokens, `.env`, `user.cnf` sont exclus par `.gitignore`.
- Le compte MariaDB du rapport n'a que `SELECT` sur la base GLPI.
