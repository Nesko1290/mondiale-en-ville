"""Fichier d'etat : ne signaler que les nouveautes d'une execution a l'autre."""

from __future__ import annotations

import json
import logging
from datetime import date, datetime, timedelta
from pathlib import Path

from .models import JobOffer

log = logging.getLogger("jobwatch.state")


class SeenState:
    """Empreinte d'offre -> {first_seen, last_seen, score, titre, url}."""

    def __init__(self, path: Path):
        self.path = path
        self.entries: dict[str, dict] = {}
        self.load()

    def load(self) -> None:
        if not self.path.exists():
            log.info("premier lancement : aucun etat precedent (%s)", self.path)
            return
        try:
            self.entries = json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            log.error("etat illisible (%s), on repart de zero", exc)
            self.entries = {}

    def mark(self, offers: list[JobOffer]) -> list[JobOffer]:
        """Renseigne `is_new` / `first_seen` et met l'etat a jour."""
        today = date.today().isoformat()
        for offer in offers:
            key = offer.fingerprint
            entry = self.entries.get(key)
            if entry is None:
                offer.is_new = True
                offer.first_seen = today
                self.entries[key] = {
                    "first_seen": today,
                    "last_seen": today,
                    "titre": offer.title,
                    "employeur": offer.employer,
                    "url": offer.url,
                    "score": offer.score,
                }
            else:
                offer.is_new = False
                offer.first_seen = entry.get("first_seen", today)
                entry["last_seen"] = today
                entry["score"] = offer.score
        return offers

    def purge(self, keep_days: int) -> int:
        limit = date.today() - timedelta(days=keep_days)
        stale = [
            key
            for key, entry in self.entries.items()
            if _as_date(entry.get("last_seen")) and _as_date(entry["last_seen"]) < limit
        ]
        for key in stale:
            del self.entries[key]
        return len(stale)

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(
            json.dumps(self.entries, ensure_ascii=False, indent=1, sort_keys=True),
            encoding="utf-8",
        )
        tmp.replace(self.path)
        log.info("etat enregistre : %d offres connues (%s)", len(self.entries), self.path)


def _as_date(value) -> date | None:
    try:
        return datetime.fromisoformat(str(value)).date()
    except (ValueError, TypeError):
        return None
