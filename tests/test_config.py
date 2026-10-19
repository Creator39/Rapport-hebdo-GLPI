from pathlib import Path

import pytest

from rapport_glpi.config import Settings, lire_fichier_env

WEBHOOK_OK = "https://discord.com/api/webhooks/123/abc"

VALIDE = {
    "DB_HOST": "10.0.0.5",
    "DB_PORT": "3306",
    "DB_NAME": "glpi",
    "DB_USER": "rapport",
    "DB_PASSWORD": "secret",
    "DISCORD_WEBHOOK_URL": WEBHOOK_OK,
}


def test_configuration_valide():
    s = Settings.depuis_variables(VALIDE)

    assert s.db_host == "10.0.0.5"
    assert s.db_port == 3306
    assert s.db_user == "rapport"


def test_port_par_defaut():
    env = {k: v for k, v in VALIDE.items() if k != "DB_PORT"}

    assert Settings.depuis_variables(env).db_port == 3306


def test_variables_manquantes_listees():
    env = {k: v for k, v in VALIDE.items() if k not in ("DB_PASSWORD", "DB_HOST")}

    with pytest.raises(ValueError) as erreur:
        Settings.depuis_variables(env)

    assert "DB_PASSWORD" in str(erreur.value)
    assert "DB_HOST" in str(erreur.value)


def test_webhook_invalide_refuse():
    env = {**VALIDE, "DISCORD_WEBHOOK_URL": "https://example.com/hook"}

    with pytest.raises(ValueError, match="webhook Discord"):
        Settings.depuis_variables(env)


def test_port_non_numerique_refuse():
    with pytest.raises(ValueError, match="DB_PORT"):
        Settings.depuis_variables({**VALIDE, "DB_PORT": "abc"})


def test_secrets_absents_de_laffichage():
    texte = repr(Settings.depuis_variables(VALIDE))

    assert "secret" not in texte
    assert WEBHOOK_OK not in texte


def test_lecture_fichier_env(tmp_path: Path):
    fichier = tmp_path / ".env"
    fichier.write_text(
        "# commentaire\n"
        "DB_HOST=10.0.0.5\n"
        'DB_PASSWORD="mot de passe"\n'
        "\n"
        "DB_NAME='glpi'\n",
        encoding="utf-8",
    )

    valeurs = lire_fichier_env(fichier)

    assert valeurs == {"DB_HOST": "10.0.0.5", "DB_PASSWORD": "mot de passe", "DB_NAME": "glpi"}
