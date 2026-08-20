"""Connecteur pour l'API publique job-room.ch (SECO / Travail.swiss).

L'API est ouverte, sans cle. Deux points d'entree sont utilises :

* ``POST /jobAdvertisements/_search`` : recherche paginee (l'en-tete
  ``X-Total-Count`` donne le nombre total de resultats) ;
* ``GET  /jobAdvertisements/{id}``    : annonce complete, seule facon
  d'obtenir la description integrale necessaire au scoring.
"""

from __future__ import annotations

import logging
from datetime import date, datetime, timedelta
from typing import Any, Iterable

from ..config import Config
from ..http import PoliteFetcher
from ..models import JobOffer, clean_html, normalize
from ..taxonomy import CORE_ROLES, FAMILIES

log = logging.getLogger("jobwatch.jobroom")

PUBLIC_URL = "https://www.job-room.ch/job-search/{id}"


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value[:10]).date()
    except ValueError:
        return None


def _pick_description(descriptions: list[dict[str, Any]]) -> dict[str, Any]:
    """Prend la version francaise si elle existe, sinon anglaise, sinon la 1re."""
    by_lang = {(d.get("languageIsoCode") or "").lower(): d for d in descriptions}
    for lang in ("fr", "en", "de", "it"):
        if lang in by_lang:
            return by_lang[lang]
    return descriptions[0] if descriptions else {}


def _to_offer(payload: dict[str, Any]) -> JobOffer | None:
    content = payload.get("jobContent") or {}
    descriptions = content.get("jobDescriptions") or []
    chosen = _pick_description(descriptions)
    title = clean_html(chosen.get("title") or "")
    if not title:
        return None

    company = content.get("company") or {}
    location = content.get("location") or {}
    employment = content.get("employment") or {}
    publication = payload.get("publication") or {}

    workload = ""
    low, high = employment.get("workloadPercentageMin"), employment.get("workloadPercentageMax")
    if low and high:
        workload = f"{low}%" if str(low) == str(high) else f"{low}-{high}%"

    url = (content.get("externalUrl") or "").strip() or PUBLIC_URL.format(
        id=payload.get("id", "")
    )

    return JobOffer(
        title=title,
        employer=(company.get("name") or "Employeur non precise").strip(),
        url=url,
        source="job-room",
        location=(location.get("city") or "").strip(),
        canton=(location.get("cantonCode") or "").strip(),
        published=_parse_date(publication.get("startDate"))
        or _parse_date(payload.get("createdTime")),
        description=clean_html((chosen.get("description") or "").replace("\\-", "-")),
        workload=workload,
        language_skills=content.get("languageSkills") or [],
        raw={"id": payload.get("id")},
    )


def _looks_relevant(offer: JobOffer) -> bool:
    """Pre-filtre bon marche avant de payer une requete de detail."""
    title = normalize(offer.title)
    if any(role in title for role in CORE_ROLES):
        return True
    for _family, (_weight, terms) in FAMILIES.items():
        if any(term in title for term in terms if len(term) > 4):
            return True
    return False


class JobRoomSource:
    def __init__(self, cfg: Config, fetcher: PoliteFetcher):
        self.cfg = cfg
        self.settings = cfg.section("jobroom")
        self.fetcher = fetcher
        self.base = self.settings.get(
            "base_url", "https://api.job-room.ch/jobadservice/api/jobAdvertisements"
        )

    # ------------------------------------------------------------------ api
    def _search_page(self, keyword: str, page: int, size: int) -> tuple[list[dict], int]:
        url = f"{self.base}/_search"
        params = {"page": page, "size": size, "sort": "date_desc"}
        body = {
            "keywords": [keyword],
            "cantonCodes": self.settings.get("cantons", []),
        }
        resp = self.fetcher.request(
            "POST", url, params=params, json=body,
            headers={"Content-Type": "application/json"},
        )
        resp.raise_for_status()
        total = int(resp.headers.get("x-total-count", 0))
        return resp.json(), total

    def _detail(self, job_id: str) -> dict[str, Any] | None:
        try:
            resp = self.fetcher.get(f"{self.base}/{job_id}")
            if resp.status_code != 200:
                return None
            return resp.json()
        except Exception as exc:  # noqa: BLE001 - une annonce ratee n'arrete rien
            log.warning("detail %s indisponible (%s)", job_id, exc)
            return None

    # ---------------------------------------------------------------- public
    def fetch(self) -> list[JobOffer]:
        if not self.settings.get("enabled", True):
            return []

        size = int(self.settings.get("page_size", 50))
        max_pages = int(self.settings.get("max_pages_per_keyword", 3))
        max_age = int(self.settings.get("max_age_days", 45))
        oldest = date.today() - timedelta(days=max_age)

        collected: dict[str, JobOffer] = {}
        for keyword in self.settings.get("keywords", []):
            page, total = 0, None
            while page < max_pages:
                try:
                    items, total = self._search_page(keyword, page, size)
                except Exception as exc:  # noqa: BLE001
                    log.error("recherche '%s' page %d echouee : %s", keyword, page, exc)
                    break
                for item in items:
                    payload = item.get("jobAdvertisement") or item
                    offer = _to_offer(payload)
                    if offer is None:
                        continue
                    if offer.published and offer.published < oldest:
                        continue
                    collected.setdefault(str(payload.get("id")), offer)
                log.info(
                    "job-room '%s' page %d : %d annonces (total %s)",
                    keyword, page, len(items), total,
                )
                page += 1
                if total is not None and (page * size) >= total:
                    break
                if not items:
                    break

        offers = list(collected.values())
        if self.settings.get("fetch_details", True):
            self._enrich(offers)
        return offers

    def _enrich(self, offers: Iterable[JobOffer]) -> None:
        """Recupere la description complete des annonces plausibles."""
        budget = int(self.settings.get("max_details", 50))
        candidates = [o for o in offers if _looks_relevant(o)][:budget]
        log.info("job-room : recuperation du detail de %d annonces", len(candidates))
        for offer in candidates:
            job_id = offer.raw.get("id")
            if not job_id:
                continue
            payload = self._detail(str(job_id))
            if not payload:
                continue
            content = payload.get("jobContent") or {}
            chosen = _pick_description(content.get("jobDescriptions") or [])
            full = clean_html((chosen.get("description") or "").replace("\\-", "-"))
            if len(full) > len(offer.description):
                offer.description = full
            # Le titre de la fiche detaillee n'est pas surligne : il est propre.
            detailed_title = clean_html(chosen.get("title") or "")
            if detailed_title:
                offer.title = detailed_title
            offer.language_skills = content.get("languageSkills") or offer.language_skills
