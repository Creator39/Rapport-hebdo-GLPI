# Architecture — Rapport hebdomadaire GLPI

> Proposition à valider avant écriture du code. Les modules et interfaces ci-dessous ne sont pas encore implémentés.

## Principes

- Fonctions pures pour tout ce qui calcule (fenêtre, indicateurs, formatage) : testables sans base ni réseau.
- Entrées/sorties (MariaDB, Discord) isolées dans deux modules seulement.
- Aucun secret dans le code : tout vient de `.env`.
- Une exécution = une semaine = un message Discord.

## Arborescence proposée

```
src/rapport_glpi/
├── __init__.py
├── __main__.py     # point d'entrée : python -m rapport_glpi
├── config.py       # lecture de .env, validation des variables
├── window.py       # fenêtre de la semaine passée (Madagascar -> UTC)
├── db.py           # requêtes MariaDB en lecture seule (PyMySQL)
├── metrics.py      # indicateurs, fonctions pures
├── report.py       # mise en forme du message et découpage à taille fixe
└── discord.py      # envoi via webhook (requests)
tests/
├── test_window.py
├── test_metrics.py
├── test_report.py
└── test_db.py      # optionnel, base de test contrôlée
```

`main.py` à la racine est supprimé. Le point d'entrée devient `src/rapport_glpi/__main__.py`, lancé par `uv run python -m rapport_glpi`.

## Interfaces entre modules

| Module | Entrée | Sortie |
|---|---|---|
| `config` | fichier `.env` | objet `Settings` (hôte, port, base, user, mot de passe, webhook, fuseau) |
| `window` | date de référence | `(debut_utc, fin_utc)`, bornes incluses/exclues |
| `db` | `Settings`, `(debut_utc, fin_utc)` | liste de `Ticket` (id, statut, dates, catégorie, équipement) |
| `metrics` | liste de `Ticket` | `Indicateurs` (créés, résolus, encours, médiane, MTTR, ratio, top pannes, catégories) |
| `report` | `Indicateurs`, fenêtre | liste de chaînes, chacune sous la limite Discord |
| `discord` | liste de chaînes, `Settings` | envoi, ou erreur explicite |
| `__main__` | — | orchestre : config → window → db → metrics → report → discord |

Les types `Ticket` et `Indicateurs` sont des dataclasses dans leur module respectif.

## Ordre de construction proposé

1. `window.py` + `tests/test_window.py` : conversion lundi 00:00 Madagascar vers UTC, bornes exclues. Premier test à écrire.
2. `metrics.py` + tests sur données fixes (dont la semaine du 27/09 au 04/10).
3. `report.py` + découpage à taille fixe.
4. `db.py` : requêtes paramétrées, testées sur base de test contrôlée.
5. `discord.py` : envoi, testé avec un faux serveur HTTP.
6. `config.py` et `__main__.py` : assemblage.
7. Cron sur l'hôte.

## Hors périmètre v1

- Modèle IA local (reporté).
- Ticket le plus long (retiré).
- Création de tickets depuis Alertmanager (projet séparé).
- Interface web.
