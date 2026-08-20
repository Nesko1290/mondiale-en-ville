"""Extraction generique des offres publiees sur une page carriere HTML.

Aucune page carriere ne se ressemble : plutot que d'ecrire un parseur par
employeur, on repere les liens qui *ressemblent* a des annonces (URL ou libelle
contenant un marqueur d'offre, intitule de poste plausible, taux d'activite,
mention f/h...), puis on ouvre chaque annonce retenue pour en lire le texte.

Un selecteur CSS peut etre fourni dans config.yaml pour les sites recalcitrants.
"""

from __future__ import annotations

import json
import logging
import re
from datetime import date, datetime
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from ..config import Employer, Source
from ..http import PoliteFetcher, RobotsDisallowed
from ..models import JobOffer, clean_html, normalize
from ..taxonomy import CORE_ROLES, FAMILIES

log = logging.getLogger("jobwatch.career")

MAX_JOBS_PER_EMPLOYER = 15

# Marqueurs d'URL d'annonce.
JOB_URL_HINT = re.compile(
    r"(offre|emploi|job|jobs|stelle|stellen|karriere|carriere|career|vacan|"
    r"position|poste|recrut|opening|hiring)", re.I
)
# Liens a ignorer quel que soit leur libelle.
LINK_BLACKLIST = re.compile(
    r"^(mailto:|tel:|javascript:|#)|(facebook|instagram|linkedin|twitter|x\.com|"
    r"youtube|tiktok)\.com|\.(pdf|jpg|jpeg|png|gif|zip|docx?)($|\?)", re.I
)
NAV_TEXT = re.compile(
    r"^(accueil|home|contact|newsletter|cookies?|mentions|impressum|privacy|"
    r"confidentialite|conditions|plan du site|sitemap|connexion|login|panier|"
    r"francais|english|deutsch|italiano|fr|en|de|it|lire la suite|en savoir plus|"
    r"voir plus|tout voir|suivant|precedent|retour|partager|postuler|apply)$", re.I
)
# Formulations signalant l'absence d'offre : evite de retenir du bruit.
NO_OPENINGS = re.compile(
    r"(aucune? (?:offre|poste|opportunit)|pas de poste (?:ouvert|vacant)|"
    r"n'?a pas de poste|aucun poste (?:ouvert|vacant|disponible)|"
    r"keine (?:offenen )?stellen|no (?:current )?(?:open )?(?:positions|vacancies))",
    re.I,
)
WORKLOAD = re.compile(r"\b\d{1,3}\s*%|\b\d{1,3}\s*[-a]\s*\d{1,3}\s*%")
GENDER_TAG = re.compile(r"\((?:h/?f|f/?h|m/?w|w/?m|m/?f)[/x]?\w?\)", re.I)

TIME_ATTRS = ("datetime", "content", "data-date")
DATE_TEXT = re.compile(
    r"(\d{1,2})[./](\d{1,2})[./](\d{4})|(\d{4})-(\d{2})-(\d{2})"
)


def _clean_text(soup: BeautifulSoup) -> str:
    # Le menu, le pied de page et les encarts lateraux d'un site parlent souvent
    # d'"evenements" ou de "communication" : les garder fausserait le scoring.
    for tag in soup(["script", "style", "noscript", "svg", "nav", "footer",
                     "header", "aside", "form"]):
        tag.decompose()
    text = soup.get_text("\n", strip=True)
    return re.sub(r"\n{3,}", "\n\n", text)


def _main_container(soup: BeautifulSoup):
    for finder in (
        lambda: soup.find("main"),
        lambda: soup.find(attrs={"role": "main"}),
        lambda: soup.find(id=re.compile(r"(^|[-_])(content|main)", re.I)),
        lambda: soup.find(class_=re.compile(r"(^|[-_ ])(content|main)", re.I)),
    ):
        node = finder()
        if node is not None:
            return node
    return soup.body or soup


def _looks_like_job_title(text: str) -> bool:
    if not (5 <= len(text) <= 140):
        return False
    if NAV_TEXT.match(text.strip()):
        return False
    norm = normalize(text)
    if any(role in norm for role in CORE_ROLES):
        return True
    if WORKLOAD.search(text) or GENDER_TAG.search(text):
        return True
    role_words = (
        "responsable", "charge", "chargee", "chef", "cheffe", "manager", "assistant",
        "assistante", "coordinateur", "coordinatrice", "directeur", "directrice",
        "specialiste", "conseiller", "conseillere", "adjoint", "collaborateur",
        "collaboratrice", "stagiaire", "apprenti", "gestionnaire", "agent", "agente",
        "technicien", "ingenieur", "avocat", "juriste", "officer", "head", "lead",
        "intern", "trainee", "praktikant", "mitarbeiter", "leiter", "consultant",
        "secretaire", "employe", "employee", "auxiliaire", "animateur", "animatrice",
    )
    if any(re.search(rf"(^|\W){w}(\W|$)", norm) for w in role_words):
        return True
    for _family, (_weight, terms) in FAMILIES.items():
        if any(term in norm for term in terms if len(term) > 5):
            return True
    return False


def _jsonld_jobs(soup: BeautifulSoup, base_url: str) -> list[dict]:
    """Annonces declarees en schema.org/JobPosting, quand le site en fournit."""
    found: list[dict] = []
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(tag.string or "")
        except (json.JSONDecodeError, TypeError):
            continue
        stack = data if isinstance(data, list) else [data]
        while stack:
            node = stack.pop()
            if not isinstance(node, dict):
                continue
            if "@graph" in node and isinstance(node["@graph"], list):
                stack.extend(node["@graph"])
            types = node.get("@type")
            types = types if isinstance(types, list) else [types]
            if "JobPosting" not in types:
                continue
            found.append(
                {
                    "title": node.get("title") or "",
                    "url": urljoin(base_url, node.get("url") or ""),
                    "description": BeautifulSoup(
                        node.get("description") or "", "lxml"
                    ).get_text(" ", strip=True),
                    "date": node.get("datePosted"),
                    "location": _jsonld_city(node),
                }
            )
    return found


def _jsonld_city(node: dict) -> str:
    loc = node.get("jobLocation")
    loc = loc[0] if isinstance(loc, list) and loc else loc
    if isinstance(loc, dict):
        address = loc.get("address")
        if isinstance(address, dict):
            return address.get("addressLocality") or ""
    return ""


def _find_date(soup: BeautifulSoup) -> date | None:
    for tag in soup.find_all(["time", "meta", "span", "div"], limit=400):
        for attr in TIME_ATTRS:
            value = tag.get(attr)
            if not value or not isinstance(value, str):
                continue
            match = DATE_TEXT.search(value)
            if match:
                return _match_to_date(match)
    match = DATE_TEXT.search(soup.get_text(" ", strip=True)[:2000])
    return _match_to_date(match) if match else None


def _match_to_date(match: re.Match) -> date | None:
    try:
        if match.group(1):
            return date(int(match.group(3)), int(match.group(2)), int(match.group(1)))
        return date(int(match.group(4)), int(match.group(5)), int(match.group(6)))
    except (ValueError, TypeError):
        return None


class CareerPageSource:
    """Collecte les offres d'une page carriere HTML."""

    def __init__(self, employer: Employer, source: Source, fetcher: PoliteFetcher):
        self.employer = employer
        self.source = source
        self.fetcher = fetcher

    def fetch(self) -> list[JobOffer]:
        url = self.source.url
        try:
            resp = self.fetcher.get(url)
        except RobotsDisallowed as exc:
            log.warning("%s : %s", self.employer.name, exc)
            return []
        except Exception as exc:  # noqa: BLE001
            log.error("%s : page carriere injoignable (%s)", self.employer.name, exc)
            return []
        if resp.status_code >= 400:
            log.warning("%s : HTTP %d sur %s", self.employer.name, resp.status_code, url)
            return []

        soup = BeautifulSoup(resp.text, "lxml")
        page_text = _clean_text(BeautifulSoup(resp.text, "lxml"))

        offers = [
            self._from_jsonld(item) for item in _jsonld_jobs(soup, resp.url)
        ]
        if offers:
            return [o for o in offers if o]

        if NO_OPENINGS.search(page_text):
            log.info("%s : aucune offre publiee actuellement", self.employer.name)
            return []

        links = self._candidate_links(soup, resp.url)
        if not links:
            log.info("%s : aucune annonce detectee sur %s", self.employer.name, url)
            return []

        collected: list[JobOffer] = []
        for link_url, title in links[:MAX_JOBS_PER_EMPLOYER]:
            offer = JobOffer(
                title=title,
                employer=self.employer.name,
                url=link_url,
                source=f"web:{self.employer.name}",
                employer_category=self.employer.category,
            )
            self._enrich(offer)
            collected.append(offer)
        return collected

    # ------------------------------------------------------------- internes
    def _from_jsonld(self, item: dict) -> JobOffer | None:
        if not item.get("title"):
            return None
        published = None
        if item.get("date"):
            try:
                published = datetime.fromisoformat(str(item["date"])[:10]).date()
            except ValueError:
                published = None
        return JobOffer(
            title=item["title"].strip(),
            employer=self.employer.name,
            url=item.get("url") or self.source.url,
            source=f"web:{self.employer.name}",
            location=item.get("location", ""),
            published=published,
            description=item.get("description", ""),
            employer_category=self.employer.category,
        )

    def _candidate_links(self, soup: BeautifulSoup, base_url: str) -> list[tuple[str, str]]:
        container = _main_container(soup)
        for tag in container(["nav", "footer", "header", "script", "style"]):
            tag.decompose()

        host = urlparse(base_url).netloc
        seen: set[str] = set()
        strong: list[tuple[str, str]] = []
        weak: list[tuple[str, str]] = []

        for anchor in container.find_all("a", href=True):
            href = anchor["href"].strip()
            if LINK_BLACKLIST.search(href):
                continue
            title = clean_html(" ".join(anchor.get_text(" ", strip=True).split()))
            if not title:
                continue
            full = urljoin(base_url, href)
            if urlparse(full).netloc not in ("", host) and not JOB_URL_HINT.search(full):
                continue
            if full.rstrip("/") == base_url.rstrip("/") or full in seen:
                continue
            if not _looks_like_job_title(title):
                continue
            seen.add(full)
            (strong if JOB_URL_HINT.search(full) else weak).append((full, title))

        # Un selecteur CSS explicite prime sur l'heuristique.
        if self.source.selector:
            picked: list[tuple[str, str]] = []
            for node in soup.select(self.source.selector):
                anchor = node if node.name == "a" else node.find("a", href=True)
                if not anchor or not anchor.get("href"):
                    continue
                picked.append(
                    (
                        urljoin(base_url, anchor["href"]),
                        " ".join(anchor.get_text(" ", strip=True).split()),
                    )
                )
            if picked:
                return picked
        return strong or weak

    def _enrich(self, offer: JobOffer) -> None:
        """Ouvre l'annonce pour recuperer son texte et sa date de parution."""
        try:
            resp = self.fetcher.get(offer.url)
        except RobotsDisallowed:
            return
        except Exception as exc:  # noqa: BLE001
            log.debug("detail %s indisponible (%s)", offer.url, exc)
            return
        if resp.status_code >= 400:
            return

        soup = BeautifulSoup(resp.text, "lxml")
        jsonld = _jsonld_jobs(soup, resp.url)
        if jsonld:
            item = jsonld[0]
            offer.description = item.get("description") or offer.description
            offer.location = item.get("location") or offer.location
            if item.get("date"):
                try:
                    offer.published = datetime.fromisoformat(str(item["date"])[:10]).date()
                except ValueError:
                    pass
            return

        body = _main_container(soup)
        offer.description = _clean_text(body)[:12000]
        offer.raw["page_lang"] = (soup.html.get("lang") if soup.html else "") or ""
        offer.published = offer.published or _find_date(soup)
        workload = WORKLOAD.search(offer.title) or WORKLOAD.search(offer.description[:600])
        if workload:
            offer.workload = workload.group(0).replace(" ", "")
