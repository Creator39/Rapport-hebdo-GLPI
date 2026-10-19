"""Accès MariaDB en lecture seule. Ce module contient le type Ticket ; les requêtes arrivent dans une étape ultérieure."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Ticket:
    id: int
    statut: str
    date_creation: datetime
    date_resolution: datetime | None
    categorie: str | None
    equipement: str | None
