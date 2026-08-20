"""Notation des offres de 0 a 100 selon le profil decrit dans config.yaml."""

from __future__ import annotations

import re
from collections import Counter

from .config import Config
from .models import JobOffer, normalize, title_key
from .taxonomy import CORE_ROLES, FAMILIES, OFF_DOMAIN_TITLE, STOPWORDS

CEFR = {"a1": 1, "a2": 2, "b1": 3, "b2": 4, "c1": 5, "c2": 6}

# Niveaux renvoyes par l'API job-room, ramenes a une echelle CEFR approximative.
AVAM_LEVELS = {
    "BASIC_KNOWLEDGE": 2,
    "INTERMEDIATE": 3,
    "GOOD": 4,
    "VERY_GOOD": 5,
    "PROFICIENT": 6,
    "NATIVE_SPEAKER": 6,
}

# --------------------------------------------------------------------- langue
_DE_WORDS = r"(?:allemand|allemande|deutsch|german|schweizerdeutsch|suisse allemand)"
_DE_NEARBY = 80  # fenetre de caracteres autour du mot "allemand"

_DE_QUALIFIERS = [
    (6, r"langue maternelle|muttersprache|bilingue|native|zweisprachig"),
    (5, r"tres bonn?e?s? (?:connaissances|maitrise)|courant|excellente maitrise|"
        r"verhandlungssicher|sehr gute"),
    (4, r"bonn?e?s? (?:connaissances|maitrise)|gute kenntnisse|solides connaissances|"
        r"tres bon niveau"),
    (3, r"connaissances|kenntnisse|niveau intermediaire|bon niveau"),
    (2, r"notions|grundkenntnisse|bases"),
]
_DE_OPTIONAL = r"un atout|un plus|un avantage|serait un|apprecie|souhaite|von vorteil|bienvenu"


def german_requirement(offer: JobOffer) -> tuple[int | None, bool]:
    """Renvoie (niveau CEFR exige, est_optionnel).

    Le niveau vaut None quand l'annonce ne demande pas d'allemand.
    """
    # 1) Donnees structurees de job-room, les plus fiables.
    structured: int | None = None
    for skill in offer.language_skills or []:
        if (skill.get("languageIsoCode") or "").lower() != "de":
            continue
        levels = [
            AVAM_LEVELS.get(skill.get(k) or "", 0)
            for k in ("spokenLevel", "writtenLevel")
        ]
        if max(levels) > 0:
            structured = max(levels)

    text = normalize(offer.text)
    optional = False
    textual: int | None = None

    for match in re.finditer(_DE_WORDS, text):
        start = max(0, match.start() - _DE_NEARBY)
        window = text[start : match.end() + _DE_NEARBY]
        if re.search(_DE_OPTIONAL, window):
            optional = True
            level = None
        else:
            level = None
        # Niveau CEFR explicite : "allemand c1", "deutsch b2"
        cefr = re.search(r"\b([abc][12])\b", window)
        if cefr:
            level = CEFR[cefr.group(1)]
        else:
            for value, pattern in _DE_QUALIFIERS:
                if re.search(pattern, window):
                    level = value
                    break
            if level is None:
                level = 4  # allemand cite sans precision : on suppose B2
        if not optional or textual is None:
            textual = max(textual or 0, level)

    if structured is not None and textual is not None:
        return max(structured, textual), optional and structured <= 3
    if structured is not None:
        return structured, False
    return textual, optional


# Mots outils propres a chaque langue : suffisent a savoir dans quelle langue
# l'annonce est redigee, ce qui est en soi une exigence linguistique.
_DE_MARKERS = re.compile(
    r"\b(und|die|der|das|den|dem|ein|eine|einen|ist|sind|wir|sie|mit|fur|von|"
    r"bei|nach|auch|sowie|ihre|unser|unsere|stelle|aufgaben|kenntnisse)\b"
)
_FR_MARKERS = re.compile(
    r"\b(et|le|la|les|des|une|un|vous|nous|pour|avec|dans|sur|votre|notre|"
    r"est|sont|poste|missions|profil|experience)\b"
)


def written_in_german(text: str) -> bool:
    norm = normalize(text)
    if len(norm) < 120:
        return False
    de = len(_DE_MARKERS.findall(norm))
    fr = len(_FR_MARKERS.findall(norm))
    return de >= 8 and de > fr * 1.5


def score_german(offer: JobOffer, comfortable: int = 4) -> tuple[float, str]:
    level, optional = german_requirement(offer)
    if level is None and written_in_german(offer.text):
        # Annonce entierement en allemand : le poste se travaille en allemand,
        # meme si aucun niveau n'est formellement demande.
        level, optional = 5, False
        return 0.2, "annonce redigee en allemand"
    if level is None:
        return 1.0, "aucun allemand exige"
    if optional:
        return 0.9, "allemand souhaite mais pas exige"
    if level <= 3:
        return 1.0, "allemand <= B1"
    if level <= comfortable:
        return 0.7, "allemand ~B2"
    if level == 5:
        return 0.25, "allemand C1 exige"
    return 0.0, "allemand C2 / langue maternelle"


# ----------------------------------------------------------------- experience
_YEARS = re.compile(
    r"(?:(\d{1,2})\s*(?:a|-|et|bis|to|jusqu a)\s*)?(\d{1,2})\s*\+?\s*"
    r"(?:ans?|annees?|jahre?n?|years?)\b"
)
_EXP_CONTEXT = re.compile(r"experience|erfahrung|pratique professionnelle|anciennete")


def parse_experience(text: str) -> tuple[int, int] | None:
    """Extrait la fourchette d'annees d'experience demandee."""
    norm = normalize(text)
    best: tuple[int, int] | None = None
    for match in _YEARS.finditer(norm):
        window = norm[max(0, match.start() - 90) : match.end() + 60]
        if not _EXP_CONTEXT.search(window):
            continue
        low = int(match.group(1)) if match.group(1) else int(match.group(2))
        high = int(match.group(2))
        if low > high:
            low, high = high, low
        if high > 40:
            continue
        if best is None or low < best[0]:
            best = (low, high)
    return best


def score_experience(offer: JobOffer, wanted: tuple[int, int] = (1, 5)) -> tuple[float, str]:
    title = normalize(offer.title)
    parsed = parse_experience(offer.text)

    if parsed:
        low, high = parsed
        if low <= wanted[1]:
            return (1.0 if low >= 1 else 0.9), f"{low}-{high} ans demandes"
        if low <= 7:
            return 0.5, f"{low}-{high} ans demandes (au-dessus du profil)"
        if low <= 9:
            return 0.3, f"{low}-{high} ans demandes"
        return 0.15, f"{low}+ ans demandes"

    if re.search(r"\b(stage|stagiaire|apprenti|apprentissage|praktikum|internship)\b", title):
        return 0.2, "stage / apprentissage"
    if re.search(r"\b(directeur|directrice|director|head of|chief|responsable general)\b", title):
        return 0.4, "poste de direction"
    if re.search(r"\bsenior\b", title):
        return 0.6, "poste senior"
    if re.search(r"\b(junior|assistant|assistante|auxiliaire)\b", title):
        return 0.85, "poste junior"
    return 0.7, "experience non precisee"


# ------------------------------------------------------------------- missions
def score_missions(offer: JobOffer) -> tuple[float, str, bool]:
    """Renvoie (score 0-1, libelle, metier_hors_profil)."""
    title = title_key(offer.title)
    body = normalize(offer.text)

    title_score = 0.0
    matched_role = ""
    for role, weight in CORE_ROLES.items():
        if role in title and weight > title_score:
            title_score, matched_role = weight, role
    if not title_score:
        # Role cite dans le corps de l'annonce seulement : moitie des points.
        for role, weight in CORE_ROLES.items():
            if role in body and weight * 0.5 > title_score:
                title_score, matched_role = weight * 0.5, role

    hit_families: list[str] = []
    family_score = 0.0
    for family, (weight, terms) in FAMILIES.items():
        hits = sum(1 for term in terms if term in body)
        if hits:
            hit_families.append(family)
            family_score += weight * min(hits, 3) / 3
    body_score = min(1.0, family_score / 2.5)

    score = 0.6 * title_score + 0.4 * body_score

    off_domain = next((w for w in OFF_DOMAIN_TITLE if w in title), "")
    if off_domain and title_score < 0.5:
        return score * 0.15, f"metier hors profil ({off_domain})", True

    label = f"role: {matched_role or 'aucun'}; themes: {', '.join(hit_families) or 'aucun'}"
    return min(1.0, score), label, False


# ---------------------------------------------------------------- geographie
def score_location(offer: JobOffer, cfg: Config) -> tuple[float, str]:
    cities = cfg.tier_map("location_tiers")
    cantons = cfg.tier_map("cantons_tiers")

    city = normalize(offer.location)
    if city:
        if city in cities:
            return cities[city], offer.location
        for name, value in cities.items():
            if name and (name in city or city in name):
                return value, offer.location

    canton = normalize(offer.canton)
    if canton in cantons:
        return cantons[canton], f"canton {offer.canton}"

    # Aucun champ "lieu" : on cherche une ville connue citee dans l'annonce.
    body = normalize(offer.text)
    best: tuple[float, str] | None = None
    for name, value in cities.items():
        if len(name) > 4 and re.search(rf"(^|\W){re.escape(name)}(\W|$)", body):
            if best is None or value > best[0]:
                best = (value, name)
    if best:
        return best[0], f"{best[1]} (cite dans l'annonce)"

    if re.search(r"teletravail|remote|home office|100% a distance", body):
        return 0.8, "teletravail"
    if offer.location:
        return 0.15, offer.location
    # Lieu reellement inconnu : note neutre, pour ne pas enterrer une offre
    # d'un employeur dont on sait qu'il est dans la region.
    return 0.4, "lieu inconnu"


# ----------------------------------------------------------------- employeur
def score_employer(offer: JobOffer, cfg: Config) -> tuple[float, str, bool]:
    """Renvoie (score 0-1, libelle, employeur_sur_liste_noire)."""
    employer = normalize(offer.employer)
    for blocked in cfg.blocklist:
        if blocked and blocked in employer:
            return 0.0, f"agence de placement ({offer.employer})", True

    tiers = cfg.tier_map("employer_tiers")
    category = normalize(offer.employer_category)
    if category and category in tiers:
        return tiers[category], offer.employer_category, False

    # Categorie inconnue : on devine a partir du nom de l'employeur.
    guesses = [
        (r"festival|salon|expo|congres|palexpo|foire|event", "evenementiel"),
        (r"musee|theatre|opera|fondation|orchestre|culture", "institution_culturelle"),
        (r"horlog|watch|joaill|montre|luxe", "horlogerie"),
        (r"etude|avocat|law|legal|notaire", "etude_avocats"),
        (r"commune|ville de|etat de|canton|administration|hopital|universite", "secteur_public"),
        (r"agence|communication sa|marketing sa", "agence_communication"),
        (r"onu|un |oms|who|cern|croix rouge|organisation internationale", "organisation_internationale"),
    ]
    for pattern, guessed in guesses:
        if re.search(pattern, employer):
            return tiers.get(guessed, 0.7), f"{guessed} (deduit)", False
    return 0.6, "employeur non categorise", False


# ------------------------------------------------------------------- mots-cles
_WORD = re.compile(r"[a-z][a-z0-9]{3,}")


def extract_keywords(offer: JobOffer, limit: int = 3) -> list[str]:
    """Trois expressions de l'annonce a reprendre dans la lettre de motivation.

    On privilegie le vocabulaire metier reellement present dans le texte, puis
    on complete avec les termes les plus frequents hors mots vides.
    """
    body = normalize(offer.text)
    title = normalize(offer.title)
    picked: list[str] = []

    def add(term: str) -> None:
        if not term:
            return
        for existing in picked:
            if term in existing or existing in term:
                return
        picked.append(term)

    # 1) Expressions metier multi-mots, les plus parlantes dans une lettre.
    domain_terms: list[tuple[int, str]] = []
    for _family, (weight, terms) in FAMILIES.items():
        for term in terms:
            if len(term) < 5 or term not in body:
                continue
            occurrences = body.count(term)
            bonus = 3 if term in title else 0
            multi = 2 if " " in term else 0
            domain_terms.append((occurrences + bonus + multi + int(weight * 2), term))
    for _rank, term in sorted(domain_terms, reverse=True):
        add(term)
        if len(picked) >= limit:
            return picked[:limit]

    # 2) Complement : termes frequents de l'annonce hors mots vides.
    counts = Counter(
        word for word in _WORD.findall(body) if word not in STOPWORDS and len(word) > 4
    )
    for word, _count in counts.most_common(20):
        add(word)
        if len(picked) >= limit:
            break
    return picked[:limit]


# ------------------------------------------------------------------- synthese
def score_offer(offer: JobOffer, cfg: Config) -> JobOffer:
    weights = cfg.weights
    profile = cfg.section("profile")
    wanted = tuple(profile.get("experience_ok_range", [1, 5]))  # type: ignore[assignment]
    comfortable = CEFR.get(
        str(profile.get("german_max_comfortable", "B2")).lower(), 4
    )

    missions, missions_label, off_domain = score_missions(offer)
    experience, experience_label = score_experience(offer, wanted)  # type: ignore[arg-type]
    german, german_label = score_german(offer, comfortable)
    location, location_label = score_location(offer, cfg)
    employer, employer_label, blocked = score_employer(offer, cfg)

    total = (
        missions * weights["missions"]
        + experience * weights["experience"]
        + german * weights["allemand"]
        + location * weights["localisation"]
        + employer * weights["employeur"]
    )

    # Le critere "missions" fait office de porte : une annonce sans lien avec
    # le profil ne doit pas remonter grace au lieu ou a l'employeur.
    if missions < 0.25:
        total *= max(0.3, missions / 0.25)

    offer.score = int(round(total))
    offer.score_detail = {
        "missions": round(missions * weights["missions"], 1),
        "experience": round(experience * weights["experience"], 1),
        "allemand": round(german * weights["allemand"], 1),
        "localisation": round(location * weights["localisation"], 1),
        "employeur": round(employer * weights["employeur"], 1),
    }
    offer.raw["score_labels"] = {
        "missions": missions_label,
        "experience": experience_label,
        "allemand": german_label,
        "localisation": location_label,
        "employeur": employer_label,
    }
    offer.raw["off_domain"] = off_domain
    offer.raw["blocked_employer"] = blocked
    offer.keywords = extract_keywords(offer)
    return offer
