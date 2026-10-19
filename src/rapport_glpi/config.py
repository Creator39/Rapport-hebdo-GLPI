"""Configuration lue depuis le fichier .env (jamais versionné)."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

WEBHOOK_PREFIXE = "https://discord.com/api/webhooks/"
VARIABLES_OBLIGATOIRES = ("DB_HOST", "DB_NAME", "DB_USER", "DB_PASSWORD", "DISCORD_WEBHOOK_URL")


def lire_fichier_env(chemin: Path) -> dict[str, str]:
    """Parse un fichier .env simple : lignes CLE=VALEUR, commentaires '#' ignorés."""
    valeurs: dict[str, str] = {}
    for ligne in chemin.read_text(encoding="utf-8").splitlines():
        ligne = ligne.strip()
        if not ligne or ligne.startswith("#") or "=" not in ligne:
            continue
        cle, valeur = ligne.split("=", 1)
        valeurs[cle.strip()] = valeur.strip().strip('"').strip("'")
    return valeurs


@dataclass(frozen=True)
class Settings:
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str = field(repr=False)
    discord_webhook_url: str = field(repr=False)

    @classmethod
    def depuis_variables(cls, env: Mapping[str, str]) -> "Settings":
        manquantes = [v for v in VARIABLES_OBLIGATOIRES if not env.get(v)]
        if manquantes:
            raise ValueError(f"Variables manquantes dans .env : {', '.join(manquantes)}")

        webhook = env["DISCORD_WEBHOOK_URL"]
        if not webhook.startswith(WEBHOOK_PREFIXE):
            raise ValueError("DISCORD_WEBHOOK_URL n'est pas un webhook Discord valide")

        try:
            port = int(env.get("DB_PORT", "3306"))
        except ValueError as erreur:
            raise ValueError("DB_PORT doit être un nombre") from erreur

        return cls(
            db_host=env["DB_HOST"],
            db_port=port,
            db_name=env["DB_NAME"],
            db_user=env["DB_USER"],
            db_password=env["DB_PASSWORD"],
            discord_webhook_url=webhook,
        )
