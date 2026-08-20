"""Flux RSS / Atom des employeurs cibles."""

from __future__ import annotations

import logging
from datetime import date, datetime

import feedparser
from bs4 import BeautifulSoup

from ..config import Employer, Source
from ..http import PoliteFetcher, RobotsDisallowed
from ..models import JobOffer, clean_html

log = logging.getLogger("jobwatch.rss")


def _entry_date(entry) -> date | None:
    for key in ("published_parsed", "updated_parsed"):
        parsed = entry.get(key)
        if parsed:
            return date(parsed.tm_year, parsed.tm_mon, parsed.tm_mday)
    for key in ("published", "updated", "date"):
        value = entry.get(key)
        if value:
            try:
                return datetime.fromisoformat(str(value)[:10]).date()
            except ValueError:
                continue
    return None


class RssSource:
    """Un flux RSS peut melanger actualites et offres : le tri se fait au scoring."""

    def __init__(self, employer: Employer, source: Source, fetcher: PoliteFetcher):
        self.employer = employer
        self.source = source
        self.fetcher = fetcher

    def fetch(self) -> list[JobOffer]:
        try:
            resp = self.fetcher.get(self.source.url)
        except RobotsDisallowed as exc:
            log.warning("%s : %s", self.employer.name, exc)
            return []
        except Exception as exc:  # noqa: BLE001
            log.error("%s : flux injoignable (%s)", self.employer.name, exc)
            return []
        if resp.status_code >= 400:
            log.warning("%s : HTTP %d sur le flux", self.employer.name, resp.status_code)
            return []

        parsed = feedparser.parse(resp.content)
        offers: list[JobOffer] = []
        for entry in parsed.entries:
            title = clean_html(entry.get("title") or "")
            if not title:
                continue
            summary_html = entry.get("summary") or ""
            if entry.get("content"):
                summary_html = entry["content"][0].get("value", summary_html)
            description = BeautifulSoup(summary_html, "lxml").get_text(" ", strip=True)
            offers.append(
                JobOffer(
                    title=title,
                    employer=self.employer.name,
                    url=(entry.get("link") or self.source.url).strip(),
                    source=f"rss:{self.employer.name}",
                    published=_entry_date(entry),
                    description=description,
                    employer_category=self.employer.category,
                )
            )
        log.info("%s : %d entrees dans le flux", self.employer.name, len(offers))
        return offers
