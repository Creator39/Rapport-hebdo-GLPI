from datetime import datetime, timezone

from rapport_glpi.metrics import Indicateurs
from rapport_glpi.report import LIMITE_DISCORD, decouper, formater_rapport

DEBUT = datetime(2026, 9, 27, 21, 0, tzinfo=timezone.utc)  # lundi 28/09 00:00 MG
FIN = datetime(2026, 10, 4, 21, 0, tzinfo=timezone.utc)  # lundi 05/10 00:00 MG, exclu


def indicateurs(**kwargs):
    base = dict(
        crees=2,
        resolus=1,
        clos=0,
        encours=1,
        mediane_jours=None,
        mttr_jours=None,
        ratio_resolus_encours=1.0,
        top_pannes=[],
        categories={},
    )
    base.update(kwargs)
    return Indicateurs(**base)


def test_entete_avec_dates_locales_inclusives():
    texte = formater_rapport(indicateurs(), DEBUT, FIN)

    assert "du 28/09/2026 au 04/10/2026" in texte


def test_compteurs_affiches():
    texte = formater_rapport(indicateurs(crees=2, resolus=1, clos=3, encours=4), DEBUT, FIN)

    assert "- Tickets créés : 2" in texte
    assert "- Résolus : 1" in texte
    assert "- Clos : 3" in texte
    assert "- En cours : 4" in texte


def test_mediane_absente_affiche_explication():
    texte = formater_rapport(indicateurs(mediane_jours=None), DEBUT, FIN)

    assert "moins de 5 tickets résolus" in texte


def test_mediane_entiere_et_mttr_formates():
    texte = formater_rapport(indicateurs(mediane_jours=2, mttr_jours=2.5), DEBUT, FIN)

    assert "Temps médian de résolution : 2 jour(s)" in texte
    assert "MTTR) : 2.5 jour(s)" in texte


def test_ratio_sans_encours_affiche_na():
    texte = formater_rapport(indicateurs(ratio_resolus_encours=None), DEBUT, FIN)

    assert "Ratio résolus / en cours : n/a" in texte


def test_top_pannes_et_categories():
    ind = indicateurs(
        top_pannes=[("srv-a", 3)],
        categories={"Réseau": 2, "Non catégorisé": 1},
    )

    texte = formater_rapport(ind, DEBUT, FIN)

    assert "- srv-a : 3 pannes" in texte
    assert "- Non catégorisé : 1" in texte
    assert "- Réseau : 2" in texte


def test_sections_vides_affichent_aucun():
    texte = formater_rapport(indicateurs(), DEBUT, FIN)

    assert "- Aucun\n" in texte
    assert texte.endswith("- Aucune")


def test_message_court_reste_en_un_seul_morceau():
    assert decouper("bonjour", 2000) == ["bonjour"]


def test_decoupe_entre_les_lignes_sans_depasser_la_limite():
    lignes = [f"ligne {i} " + "x" * 30 for i in range(10)]
    message = "\n".join(lignes)

    morceaux = decouper(message, limite=100)

    assert all(len(m) <= 100 for m in morceaux)
    assert len(morceaux) > 1
    # Aucune ligne n'est coupée : chaque morceau contient des lignes entières
    assert "\n".join(morceaux) == message


def test_ligne_trop_longue_est_coupee_en_plein_milieu():
    message = "a" * 250

    morceaux = decouper(message, limite=100)

    assert morceaux == ["a" * 100, "a" * 100, "a" * 50]


def test_limite_discord_par_defaut():
    assert LIMITE_DISCORD == 2000
    assert all(len(m) <= 2000 for m in decouper("y" * 4500))


def test_limite_invalide_refusee():
    import pytest

    with pytest.raises(ValueError):
        decouper("abc", limite=0)
