from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import pytest

from rapport_glpi.window import previous_week_window

MG = ZoneInfo("Indian/Antananarivo")


def test_lundi_matin_donne_la_semaine_precedente_en_utc():
    # Lundi 19/10/2026 00:05 heure de Madagascar, soit dimanche 18/10 21:05 UTC
    now = datetime(2026, 10, 19, 0, 5, tzinfo=MG)

    debut, fin = previous_week_window(now)

    assert debut == datetime(2026, 10, 11, 21, 0, tzinfo=timezone.utc)
    assert fin == datetime(2026, 10, 18, 21, 0, tzinfo=timezone.utc)


def test_execution_cron_en_utc_donne_la_meme_fenetre():
    # Cron : dimanche 18/10 21:05 UTC
    now = datetime(2026, 10, 18, 21, 5, tzinfo=timezone.utc)

    assert previous_week_window(now) == previous_week_window(
        datetime(2026, 10, 19, 0, 5, tzinfo=MG)
    )


def test_semaine_de_reference_du_projet():
    # Semaine test de la spécification : 27/09 21:00 UTC -> 04/10 21:00 UTC
    now = datetime(2026, 10, 5, 0, 5, tzinfo=MG)

    debut, fin = previous_week_window(now)

    assert debut == datetime(2026, 9, 27, 21, 0, tzinfo=timezone.utc)
    assert fin == datetime(2026, 10, 4, 21, 0, tzinfo=timezone.utc)


def test_dimanche_soir_est_dans_la_semaine_en_cours():
    # Dimanche 18/10 23:59 heure de Madagascar : semaine en cours = 12/10 au 19/10
    now = datetime(2026, 10, 18, 23, 59, tzinfo=MG)

    debut, fin = previous_week_window(now)

    assert debut == datetime(2026, 10, 4, 21, 0, tzinfo=timezone.utc)
    assert fin == datetime(2026, 10, 11, 21, 0, tzinfo=timezone.utc)


def test_fin_exclue_et_debut_inclus():
    now = datetime(2026, 10, 19, 0, 5, tzinfo=MG)

    debut, fin = previous_week_window(now)

    assert debut < fin
    assert (fin - debut).days == 7


def test_datetime_naive_refusee():
    with pytest.raises(ValueError):
        previous_week_window(datetime(2026, 10, 19, 0, 5))
