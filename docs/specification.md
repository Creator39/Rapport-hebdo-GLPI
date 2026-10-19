# Spécification — Rapport hebdomadaire GLPI

Document de référence. Chaque règle ici a été validée explicitement ; ne pas la modifier sans décision écrite.

## Périmètre v1

- Uniquement les tickets créés manuellement.
- L'automatisation de création de tickets depuis Alertmanager est un projet séparé.
- Le ticket le plus long de la semaine est retiré du rapport v1.
- Le modèle IA local est reporté.

## Population

- Tickets créés pendant la fenêtre de la semaine passée uniquement.
- Fenêtre : lundi 00:00 heure de Madagascar (UTC+3) jusqu'au lundi suivant 00:00 exclu, convertie en UTC pour la requête (la base est en UTC).

## Statuts GLPI

- **Résolu** : statut « Résolu » uniquement.
- **Clos** : statut « Clos », quelle que soit la date de résolution. Affiché séparément, toujours présent dans le rapport.
- **Encours** : tickets de la semaine passée encore non terminés à l'envoi, y compris « En attente » (proche de « En cours »).

## Indicateurs

- Tickets créés.
- Tickets résolus.
- Encours.
- Temps médian de résolution, calculé sur les résolus uniquement, seuil minimum de 5 tickets résolus.
- Temps moyen de résolution (MTTR).
- Ratio résolus / en cours, pour préparer la semaine suivante.
- Top des équipements défaillants : seuil de 2 pannes minimum par machine sur la semaine.
- Répartition par catégorie d'incident.

Durée de résolution = date de résolution − date de création, en temps calendaire (dates seules). Pas de répartition par gravité : le champ priorité est presque toujours « moyen » par défaut.

## Envoi

- Discord, découpage du message à taille fixe pour respecter la limite.
- Adresses IP et lieux affichés : canal admin uniquement.

## Données et accès

- Compte MariaDB `rapport` en lecture seule, `SELECT` sur la base GLPI uniquement, vérifié avec `SHOW GRANTS`.
- Le compte de l'application GLPI ne doit pas servir au rapport.

## Tests

- Données de test contrôlées, pas de copie implicite de la production.
- Semaine de test de référence : fenêtre UTC 2026-09-27 21:00 → 2026-10-04 21:00 (2 créés, 1 résolu, 1 en cours, 0 clos), à reproduire avec des données fixes.

## Mesure de succès

- Le rapport arrive chaque lundi sans intervention manuelle.
- Les chiffres correspondent à une vérification manuelle faite sur une semaine réelle, avant la mise en service.
- La sortie va uniquement vers Discord (canal admin).
- Le webhook Discord est stocké dans `.env` uniquement, jamais dans le dépôt ni dans la documentation.

## Points ouverts

- Tickets de test 33, 34, 36 encore présents en base de test : décision à prendre.
- Nommage des fichiers de sortie : granularité à trancher (jour ou heure).
