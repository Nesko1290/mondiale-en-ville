"""Structures de donnees partagees par tout le pipeline."""

from __future__ import annotations

import hashlib
import html
import re
import unicodedata
from dataclasses import dataclass, field, asdict
from datetime import date
from typing import Any


_TAGS = re.compile(r"<[^>]{1,80}>")


def clean_html(text: str) -> str:
    """Retire le balisage et decode les entites.

    L'API job-room renvoie les termes trouves entoures de <em> dans les
    resultats de recherche : sans nettoyage, ils polluent titres et CSV.
    """
    if not text:
        return ""
    return re.sub(r"[ \t]{2,}", " ", html.unescape(_TAGS.sub("", text))).strip()


def strip_accents(text: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c)
    )


def normalize(text: str) -> str:
    """Minuscules, sans accents, ponctuation reduite a des espaces simples."""
    text = strip_accents(text or "").lower()
    text = re.sub(r"[^a-z0-9%+]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


# Elements retires du titre normalise avant empreinte : taux d'activite,
# mentions f/h, type de contrat. "80-100%" devient "80 100%" apres
# normalisation, d'ou les alternatives sans tiret.
_TITLE_NOISE = re.compile(
    r"(?<![a-z0-9])(\d{1,3}\s+\d{1,3}\s*%|\d{1,3}\s*%"
    r"|[fhmwdx](\s+[fhmwdx])+"
    r"|cdi|cdd|temps partiel|temps plein|a pourvoir|urgent|nouveau|new)"
    r"(?![a-z0-9])"
)
# Lettres isolees laissees par l'ecriture inclusive : "charge.e" -> "charge e".
_LONE_LETTER = re.compile(r"(?<![a-z0-9])[a-z](?![a-z0-9])")


def title_key(title: str) -> str:
    """Cle de titre stable : variantes de taux, de genre et de contrat ecrasees."""
    key = _TITLE_NOISE.sub(" ", normalize(title))
    key = _LONE_LETTER.sub(" ", key)
    return re.sub(r"\s+", " ", key).strip()


@dataclass
class JobOffer:
    """Une offre normalisee, quelle que soit sa source."""

    title: str
    employer: str
    url: str
    source: str                      # 'job-room' | 'rss:<nom>' | 'web:<nom>'
    location: str = ""
    canton: str = ""
    published: date | None = None
    description: str = ""
    workload: str = ""
    employer_category: str = ""      # renseigne depuis config.yaml
    language_skills: list[dict[str, Any]] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    # Rempli par le scoring
    score: int = 0
    score_detail: dict[str, float] = field(default_factory=dict)
    keywords: list[str] = field(default_factory=list)
    is_new: bool = True
    first_seen: str = ""

    @property
    def text(self) -> str:
        """Titre + description, pour toutes les analyses textuelles."""
        return f"{self.title}\n{self.description}"

    @property
    def fingerprint(self) -> str:
        """Empreinte de deduplication : titre + employeur + date de parution."""
        base = "|".join(
            [
                title_key(self.title),
                normalize(self.employer),
                self.published.isoformat() if self.published else "",
            ]
        )
        return hashlib.sha1(base.encode("utf-8")).hexdigest()[:16]

    @property
    def loose_key(self) -> str:
        """Cle sans date : meme poste republie a quelques jours d'intervalle."""
        return f"{normalize(self.employer)}|{title_key(self.title)}"

    def to_row(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "titre": self.title,
            "employeur": self.employer,
            "lieu": self.location or self.canton,
            "date_parution": self.published.isoformat() if self.published else "",
            "url": self.url,
            "mots_cles_lettre": " | ".join(self.keywords),
            "nouveau": "oui" if self.is_new else "non",
            "source": self.source,
            "taux": self.workload,
            "detail_score": "; ".join(
                f"{k}={v:g}" for k, v in self.score_detail.items()
            ),
        }

    def to_state(self) -> dict[str, Any]:
        d = asdict(self)
        d.pop("raw", None)
        d["published"] = self.published.isoformat() if self.published else None
        return d
