"""Orchestration : collecte -> deduplication -> scoring -> etat -> rapports."""

from __future__ import annotations

import logging
from datetime import date, timedelta
from pathlib import Path

from .config import Config, Employer
from .dedupe import deduplicate
from .http import PoliteFetcher
from .models import JobOffer
from .report import write_csv, write_markdown
from .scoring import score_offer
from .sources.ats import AtsSource
from .sources.careerpages import CareerPageSource
from .sources.feeds import RssSource
from .sources.jobroom import JobRoomSource
from .state import SeenState

log = logging.getLogger("jobwatch.pipeline")


def _web_fetcher(cfg: Config) -> PoliteFetcher:
    return PoliteFetcher(
        user_agent=cfg.user_agent,
        delay=cfg.delay,
        timeout=cfg.timeout,
        respect_robots=cfg.respect_robots,
        max_retries=cfg.max_retries,
    )


def _api_fetcher(cfg: Config) -> PoliteFetcher:
    return PoliteFetcher(
        user_agent=cfg.user_agent,
        delay=cfg.api_delay,
        timeout=cfg.timeout,
        respect_robots=cfg.respect_robots,
        max_retries=cfg.max_retries,
    )


def collect(cfg: Config, only: list[str] | None = None) -> list[JobOffer]:
    offers: list[JobOffer] = []

    if cfg.section("jobroom").get("enabled", True) and not only:
        log.info("--- API job-room.ch (SECO) ---")
        offers += JobRoomSource(cfg, _api_fetcher(cfg)).fetch()
        log.info("job-room : %d annonces collectees", len(offers))

    fetcher = _web_fetcher(cfg)
    for employer in cfg.employers:
        if not employer.enabled:
            continue
        if only and employer.name.lower() not in [o.lower() for o in only]:
            continue
        for source in employer.sources:
            before = len(offers)
            found = _fetch_source(employer, source, fetcher)
            for offer in found:
                offer.location = offer.location or employer.location
                offer.canton = offer.canton or employer.canton
            offers += found
            log.info(
                "%s (%s) : %d annonces", employer.name, source.type, len(offers) - before
            )
    return offers


def _fetch_source(employer: Employer, source, fetcher: PoliteFetcher) -> list[JobOffer]:
    try:
        if source.type == "rss":
            return RssSource(employer, source, fetcher).fetch()
        if source.type == "ats":
            return AtsSource(employer, source, fetcher).fetch()
        if source.type == "career":
            return CareerPageSource(employer, source, fetcher).fetch()
    except Exception as exc:  # noqa: BLE001 - un employeur en panne n'arrete pas la veille
        log.error("%s : source %s en echec (%s)", employer.name, source.type, exc)
        return []
    log.error("%s : type de source inconnu '%s'", employer.name, source.type)
    return []


def run(cfg: Config, only_new: bool = False, only: list[str] | None = None) -> dict:
    raw_offers = collect(cfg, only=only)
    log.info("%d annonces brutes collectees", len(raw_offers))

    offers = deduplicate(
        raw_offers, cfg.section("scoring").get("aggregator_employers")
    )

    for offer in offers:
        score_offer(offer, cfg)

    oldest = date.today() - timedelta(days=cfg.max_age_days)
    retained: list[JobOffer] = []
    rejected = {"hors_profil": 0, "agence": 0, "score": 0, "perimee": 0}
    for offer in offers:
        if offer.raw.get("off_domain"):
            rejected["hors_profil"] += 1
            continue
        if offer.raw.get("blocked_employer"):
            rejected["agence"] += 1
            continue
        if offer.published and offer.published < oldest:
            rejected["perimee"] += 1
            continue
        if offer.score < cfg.min_score:
            rejected["score"] += 1
            continue
        retained.append(offer)

    retained.sort(key=lambda o: (-o.score, o.employer, o.title))

    state = SeenState(cfg.state_path())
    state.mark(retained)
    purged = state.purge(int(cfg.section("output").get("keep_days", 90)))
    state.save()

    reported = [o for o in retained if o.is_new] if only_new else retained

    out = cfg.out_dir()
    today = date.today().isoformat()
    names = cfg.section("output")
    # En mode "nouveautes seules", on ecrit dans des fichiers distincts pour
    # ne pas ecraser le tableau complet de la journee.
    prefix = "nouveautes_" if only_new else ""
    csv_path = out / (
        prefix + names.get("csv_name", "offres_{date}.csv").format(date=today)
    )
    md_path = out / (
        prefix + names.get("markdown_name", "offres_{date}.md").format(date=today)
    )

    stats = {
        "brutes": len(raw_offers),
        "apres dedup": len(offers),
        "retenues": len(retained),
        "nouvelles": sum(1 for o in retained if o.is_new),
        "hors profil": rejected["hors_profil"],
        "agences ecartees": rejected["agence"],
        "sous le seuil": rejected["score"],
    }

    write_csv(reported, csv_path)
    write_markdown(reported, md_path, stats)
    latest = names.get("latest_markdown")
    if latest:
        write_markdown(reported, out / latest, stats)

    log.info(
        "termine : %d retenues dont %d nouvelles (%d purgees de l'etat)",
        len(retained), stats["nouvelles"], purged,
    )
    return {
        "offers": retained,
        "reported": reported,
        "stats": stats,
        "csv": csv_path,
        "markdown": md_path,
    }


def discover(url: str, cfg: Config) -> list[tuple[str, str]]:
    """Aide a la configuration : liste les liens 'carriere' d'un site."""
    import re

    from bs4 import BeautifulSoup

    fetcher = _web_fetcher(cfg)
    resp = fetcher.get(url)
    soup = BeautifulSoup(resp.text, "lxml")
    pattern = re.compile(
        r"emploi|job|carri|karriere|recrut|vacanc|stellen|nous-rejoindre|hiring", re.I
    )
    found: list[tuple[str, str]] = []
    seen: set[str] = set()
    from urllib.parse import urljoin

    for anchor in soup.find_all("a", href=True):
        text = anchor.get_text(" ", strip=True)
        href = anchor["href"]
        if not (pattern.search(href) or pattern.search(text)):
            continue
        full = urljoin(resp.url, href)
        if full in seen:
            continue
        seen.add(full)
        found.append((full, text[:70]))
    for link in soup.find_all("link", rel=True, href=True):
        rels = [r.lower() for r in link.get("rel")]
        if "alternate" in rels and "xml" in (link.get("type") or ""):
            found.append((urljoin(resp.url, link["href"]), "[flux RSS]"))
    return found
