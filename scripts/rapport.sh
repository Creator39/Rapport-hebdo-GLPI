#!/usr/bin/env bash
# Lance le rapport hebdomadaire GLPI. Appelé par cron (voir README).
# Aucun secret ici : la configuration est lue depuis .env à la racine du dépôt.
set -euo pipefail

RACINE="$(cd "$(dirname "$0")/.." && pwd)"
UV="${UV_BIN:-$HOME/.local/bin/uv}"

cd "$RACINE"
export PYTHONPATH=src
exec "$UV" run python -m rapport_glpi "$@"
