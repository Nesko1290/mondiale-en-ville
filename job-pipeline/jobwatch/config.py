"""Chargement et acces type a config.yaml."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .models import normalize


@dataclass
class Source:
    type: str                 # career | rss | ats
    url: str = ""
    platform: str = ""        # pour type=ats
    company: str = ""         # pour type=ats
    selector: str = ""        # selecteur CSS optionnel (type=career)


@dataclass
class Employer:
    name: str
    category: str = "pme"
    enabled: bool = True
    location: str = ""        # lieu par defaut si l'annonce ne le precise pas
    canton: str = ""
    sources: list[Source] = field(default_factory=list)


@dataclass
class Config:
    path: Path
    raw: dict[str, Any]

    # ------------------------------------------------------------- chargement
    @classmethod
    def load(cls, path: str | Path) -> "Config":
        path = Path(path)
        with path.open(encoding="utf-8") as fh:
            raw = yaml.safe_load(fh) or {}
        return cls(path=path, raw=raw)

    def section(self, name: str) -> dict[str, Any]:
        return self.raw.get(name) or {}

    # ---------------------------------------------------------------- acces
    @property
    def root(self) -> Path:
        return self.path.parent

    @property
    def user_agent(self) -> str:
        return self.section("http").get(
            "user_agent", "JobWatchBot/1.0 (+https://example.org)"
        )

    @property
    def delay(self) -> float:
        return float(self.section("http").get("delay_seconds", 2.0))

    @property
    def api_delay(self) -> float:
        return float(self.section("http").get("api_delay_seconds", self.delay))

    @property
    def timeout(self) -> int:
        return int(self.section("http").get("timeout_seconds", 30))

    @property
    def respect_robots(self) -> bool:
        return bool(self.section("http").get("respect_robots", True))

    @property
    def max_retries(self) -> int:
        return int(self.section("http").get("max_retries", 3))

    @property
    def employers(self) -> list[Employer]:
        out: list[Employer] = []
        for item in self.raw.get("employers") or []:
            sources = [Source(**s) for s in (item.get("sources") or [])]
            out.append(
                Employer(
                    name=item["name"],
                    category=item.get("category", "pme"),
                    enabled=bool(item.get("enabled", True)),
                    location=item.get("location", ""),
                    canton=item.get("canton", ""),
                    sources=sources,
                )
            )
        return out

    @property
    def weights(self) -> dict[str, float]:
        default = {
            "missions": 40,
            "experience": 20,
            "allemand": 15,
            "localisation": 15,
            "employeur": 10,
        }
        default.update(self.section("scoring").get("weights") or {})
        return {k: float(v) for k, v in default.items()}

    def tier_map(self, key: str) -> dict[str, float]:
        """Convertit {1.0: [a, b]} en {a: 1.0, b: 1.0} avec cles normalisees."""
        out: dict[str, float] = {}
        for value, entries in (self.section("scoring").get(key) or {}).items():
            for entry in entries or []:
                out[normalize(str(entry))] = float(value)
        return out

    @property
    def blocklist(self) -> list[str]:
        return [
            normalize(x)
            for x in (self.section("scoring").get("blocklist_employers") or [])
        ]

    @property
    def min_score(self) -> int:
        return int(self.section("filters").get("min_score", 0))

    @property
    def max_age_days(self) -> int:
        return int(self.section("filters").get("max_age_days", 60))

    # -------------------------------------------------------------- chemins
    def out_dir(self) -> Path:
        d = self.root / self.section("output").get("dir", "out")
        d.mkdir(parents=True, exist_ok=True)
        return d

    def state_path(self) -> Path:
        p = self.root / self.section("output").get("state_file", "state/seen.json")
        p.parent.mkdir(parents=True, exist_ok=True)
        return p
