"""Deduplication des offres : titre + employeur + date, avec rattrapage flou.

Une meme annonce arrive souvent deux fois : une fois par l'API job-room, une
fois par la page carriere de l'employeur, avec un titre legerement different
("Chargé·e" vs "Chargée", taux d'activite present ou non). La cle exacte
attrape la majorite des cas, la similarite de titre le reste.
"""

from __future__ import annotations

import logging
from difflib import SequenceMatcher

from .models import JobOffer, normalize

log = logging.getLogger("jobwatch.dedupe")

TITLE_SIMILARITY = 0.87
MAX_DAYS_APART = 30

# Une offre publiee sur le site de l'employeur est preferable a la meme offre
# vue via un agregateur : le lien est plus stable et la description complete.
SOURCE_PRIORITY = {"web": 3, "ats": 3, "rss": 2, "job-room": 1}


def _priority(offer: JobOffer) -> tuple[int, int]:
    kind = offer.source.split(":", 1)[0]
    return SOURCE_PRIORITY.get(kind, 0), len(offer.description)


def _merge(keep: JobOffer, other: JobOffer) -> JobOffer:
    """Complete l'offre retenue avec ce que l'autre apporte en plus."""
    if len(other.description) > len(keep.description):
        keep.description = other.description
    keep.location = keep.location or other.location
    keep.canton = keep.canton or other.canton
    keep.workload = keep.workload or other.workload
    keep.published = keep.published or other.published
    keep.employer_category = keep.employer_category or other.employer_category
    keep.language_skills = keep.language_skills or other.language_skills
    doublons = keep.raw.setdefault("doublons", [])
    if other.source not in doublons:
        doublons.append(other.source)
    return keep


def _is_aggregator(offer: JobOffer, aggregators: list[str]) -> bool:
    employer = normalize(offer.employer)
    return any(name and name in employer for name in aggregators)


def deduplicate(
    offers: list[JobOffer], aggregators: list[str] | None = None
) -> list[JobOffer]:
    """Ecarte les doublons ; `aggregators` liste les republicateurs anonymes.

    Une meme annonce apparait souvent sous le nom de l'employeur *et* sous
    celui d'un agregateur (jobup, jobs.ch...). Pour ces derniers, la
    comparaison se fait sur le titre seul, toutes entreprises confondues.
    """
    aggregators = [normalize(a) for a in (aggregators or [])]
    exact: dict[str, JobOffer] = {}
    for offer in sorted(offers, key=_priority, reverse=True):
        key = offer.fingerprint
        if key in exact:
            _merge(exact[key], offer)
        else:
            exact[key] = offer

    # Deuxieme passe : meme employeur, titre tres proche, dates rapprochees.
    # Les offres d'agregateurs sont traitees en dernier pour que le nom du
    # vrai employeur l'emporte lors de la fusion.
    kept: list[JobOffer] = []
    by_employer: dict[str, list[JobOffer]] = {}
    ordered = sorted(exact.values(), key=lambda o: _is_aggregator(o, aggregators))
    for offer in ordered:
        employer = normalize(offer.employer)
        if _is_aggregator(offer, aggregators):
            pool = kept                       # comparaison tous employeurs confondus
        else:
            pool = by_employer.get(employer, [])
        match = next((c for c in pool if _close_enough(c, offer)), None)
        if match is not None:
            _merge(match, offer)
            continue
        by_employer.setdefault(employer, []).append(offer)
        kept.append(offer)

    removed = len(offers) - len(kept)
    if removed:
        log.info("deduplication : %d doublons ecartes sur %d", removed, len(offers))
    return kept


def _close_enough(a: JobOffer, b: JobOffer) -> bool:
    from .models import title_key

    if a.published and b.published:
        if abs((a.published - b.published).days) > MAX_DAYS_APART:
            return False
    ratio = SequenceMatcher(None, title_key(a.title), title_key(b.title)).ratio()
    return ratio >= TITLE_SIMILARITY
