"""Fenêtre de la semaine passée, en heure de Madagascar puis convertie en UTC."""

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

REPORT_TZ = ZoneInfo("Indian/Antananarivo")
UTC = timezone.utc


def previous_week_window(now: datetime) -> tuple[datetime, datetime]:
    """Retourne (début, fin) en UTC pour la semaine passée.

    La semaine va du lundi 00:00 (heure de Madagascar) au lundi suivant 00:00 exclu.
    `now` doit être une datetime aware. La fenêtre est calculée à partir du
    lundi de la semaine en cours, donc `now` peut être n'importe quel instant de
    la semaine en cours (typiquement le lundi 00:05, heure de Madagascar).
    """
    if now.tzinfo is None:
        raise ValueError("now doit être une datetime aware")

    local = now.astimezone(REPORT_TZ)
    this_monday = (local - timedelta(days=local.weekday())).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    start_local = this_monday - timedelta(days=7)

    return start_local.astimezone(UTC), this_monday.astimezone(UTC)
