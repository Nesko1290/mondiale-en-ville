"""Connecteurs pour les plateformes de recrutement a API publique.

Beaucoup d'employeurs suisses delegent leurs annonces a un ATS qui expose un
JSON stable : c'est bien plus fiable que de gratter la page carriere.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Callable

from bs4 import BeautifulSoup

from ..config import Employer, Source
from ..http import PoliteFetcher
from ..models import JobOffer

log = logging.getLogger("jobwatch.ats")

ENDPOINTS: dict[str, str] = {
    "greenhouse": "https://boards-api.greenhouse.io/v1/boards/{company}/jobs?content=true",
    "lever": "https://api.lever.co/v0/postings/{company}?mode=json",
    "smartrecruiters": "https://api.smartrecruiters.com/v1/companies/{company}/postings?limit=100",
    "recruitee": "https://{company}.recruitee.com/api/offers/",
    "personio": "https://{company}.jobs.personio.de/search.json",
}


def _html_to_text(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join(_html_to_text(v) for v in value.values())
    if isinstance(value, list):
        return " ".join(_html_to_text(v) for v in value)
    return BeautifulSoup(str(value or ""), "lxml").get_text(" ", strip=True)


def _iso(value: Any):
    try:
        return datetime.fromisoformat(str(value)[:10]).date()
    except (ValueError, TypeError):
        return None


def _greenhouse(data: dict) -> list[dict]:
    return [
        {
            "title": job.get("title"),
            "url": job.get("absolute_url"),
            "location": (job.get("location") or {}).get("name", ""),
            "date": _iso(job.get("updated_at")),
            "description": _html_to_text(job.get("content")),
        }
        for job in data.get("jobs", [])
    ]


def _lever(data: list) -> list[dict]:
    return [
        {
            "title": job.get("text"),
            "url": job.get("hostedUrl"),
            "location": (job.get("categories") or {}).get("location", ""),
            "date": None,
            "description": _html_to_text(job.get("descriptionPlain") or job.get("description")),
        }
        for job in data
    ]


def _smartrecruiters(data: dict) -> list[dict]:
    out = []
    for job in data.get("content", []):
        loc = job.get("location") or {}
        out.append(
            {
                "title": job.get("name"),
                "url": f"https://jobs.smartrecruiters.com/{job.get('company', {}).get('identifier','')}/{job.get('id','')}",
                "location": loc.get("city", ""),
                "date": _iso(job.get("releasedDate")),
                "description": _html_to_text(job.get("jobAd")),
            }
        )
    return out


def _recruitee(data: dict) -> list[dict]:
    return [
        {
            "title": job.get("title"),
            "url": job.get("careers_url") or job.get("careers_apply_url"),
            "location": job.get("location", ""),
            "date": _iso(job.get("published_at")),
            "description": _html_to_text(job.get("description")),
        }
        for job in data.get("offers", [])
    ]


def _personio(data: Any) -> list[dict]:
    jobs = data if isinstance(data, list) else data.get("jobs", [])
    return [
        {
            "title": job.get("name") or job.get("title"),
            "url": job.get("url") or job.get("link"),
            "location": job.get("office") or job.get("location", ""),
            "date": _iso(job.get("createdAt")),
            "description": _html_to_text(job.get("jobDescriptions") or job.get("description")),
        }
        for job in jobs
    ]


PARSERS: dict[str, Callable[[Any], list[dict]]] = {
    "greenhouse": _greenhouse,
    "lever": _lever,
    "smartrecruiters": _smartrecruiters,
    "recruitee": _recruitee,
    "personio": _personio,
}


class AtsSource:
    def __init__(self, employer: Employer, source: Source, fetcher: PoliteFetcher):
        self.employer = employer
        self.source = source
        self.fetcher = fetcher

    def fetch(self) -> list[JobOffer]:
        platform = (self.source.platform or "").lower()
        if platform not in ENDPOINTS:
            log.error("%s : plateforme ATS inconnue '%s'", self.employer.name, platform)
            return []
        url = self.source.url or ENDPOINTS[platform].format(company=self.source.company)
        try:
            resp = self.fetcher.get(url)
            resp.raise_for_status()
            payload = resp.json()
        except Exception as exc:  # noqa: BLE001
            log.error("%s : ATS %s injoignable (%s)", self.employer.name, platform, exc)
            return []

        offers: list[JobOffer] = []
        for item in PARSERS[platform](payload):
            if not item.get("title"):
                continue
            offers.append(
                JobOffer(
                    title=str(item["title"]).strip(),
                    employer=self.employer.name,
                    url=item.get("url") or url,
                    source=f"ats:{platform}:{self.employer.name}",
                    location=item.get("location") or "",
                    published=item.get("date"),
                    description=item.get("description") or "",
                    employer_category=self.employer.category,
                )
            )
        log.info("%s : %d annonces via %s", self.employer.name, len(offers), platform)
        return offers
