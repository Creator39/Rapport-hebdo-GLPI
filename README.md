# Rapport hebdomadaire GLPI

Génère chaque semaine un rapport d'incidents à partir des tickets GLPI créés pendant la semaine passée, puis l'envoie sur Discord.

## Fonctionnement

- Exécution via cron sur l'hôte, le dimanche à 21:05 UTC (lundi 00:00 à Madagascar, UTC+3).
- Fenêtre : tickets créés du lundi 00:00 (heure de Madagascar) au lundi suivant 00:00 exclu.
- Lecture SQL directe sur MariaDB, avec un compte en lecture seule dédié.
- Envoi sur un canal Discord réservé aux administrateurs (le rapport contient des adresses IP).

Le détail des règles métier est dans [docs/specification.md](docs/specification.md).

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env_example .env   # puis renseigner les valeurs locales
```

## Tests

Les tests tournent sur des données contrôlées, jamais sur une copie de la production.

```bash
pytest tests/
```

## Sécurité

- Aucun secret dans le dépôt : mots de passe, tokens, `.env`, `user.cnf` sont exclus par `.gitignore`.
- Le compte MariaDB du rapport n'a que `SELECT` sur la base GLPI.
