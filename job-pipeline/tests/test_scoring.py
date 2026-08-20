"""Tests du scoring : chaque critere est verifie isolement."""

from datetime import date
from pathlib import Path

import pytest

from jobwatch.config import Config
from jobwatch.models import JobOffer
from jobwatch.scoring import (
    extract_keywords,
    german_requirement,
    parse_experience,
    score_experience,
    score_german,
    score_missions,
    score_offer,
    written_in_german,
)

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def cfg():
    return Config.load(ROOT / "config.yaml")


def offer(**kwargs) -> JobOffer:
    base = dict(
        title="Charge de communication",
        employer="Palexpo",
        url="https://exemple.ch/offre",
        source="web:test",
        location="Geneve",
        canton="GE",
        employer_category="evenementiel",
        published=date.today(),
        description="",
    )
    base.update(kwargs)
    return JobOffer(**base)


# --------------------------------------------------------------- experience
@pytest.mark.parametrize(
    "text, expected",
    [
        ("3 a 5 ans d'experience dans la communication", (3, 5)),
        ("au minimum 5 ans d'experience", (5, 5)),
        ("Sie bringen 10 Jahre Erfahrung mit", (10, 10)),
        ("2 years of experience in marketing", (2, 2)),
        ("un poste de 5 ans renouvelable", None),   # pas de contexte "experience"
        ("aucune indication", None),
    ],
)
def test_parse_experience(text, expected):
    assert parse_experience(text) == expected


def test_experience_dans_la_fourchette():
    score, _ = score_experience(offer(description="3 a 5 ans d'experience exiges"))
    assert score == 1.0


def test_experience_trop_elevee():
    score, label = score_experience(offer(description="12 ans d'experience exiges"))
    assert score < 0.3
    assert "12" in label


def test_experience_stage_penalisee():
    score, _ = score_experience(offer(title="Stagiaire communication"))
    assert score <= 0.2


# ------------------------------------------------------------------ allemand
@pytest.mark.parametrize(
    "description, mini, maxi",
    [
        ("Francais et anglais demandes", 1.0, 1.0),
        ("Allemand un atout", 0.85, 0.95),
        ("Bonnes connaissances d'allemand", 0.6, 0.75),
        ("Allemand C1 exige", 0.2, 0.3),
        ("Allemand langue maternelle", 0.0, 0.05),
    ],
)
def test_score_allemand(description, mini, maxi):
    score, _ = score_german(offer(description=description))
    assert mini <= score <= maxi


def test_allemand_depuis_les_donnees_structurees():
    o = offer(language_skills=[{"languageIsoCode": "de", "spokenLevel": "PROFICIENT"}])
    level, _ = german_requirement(o)
    assert level == 6
    assert score_german(o)[0] == 0.0


def test_annonce_redigee_en_allemand_est_penalisee():
    texte = (
        "Wir suchen eine Mitarbeiterin fur die Kommunikation. Sie sind fur die "
        "Betreuung unserer Kunden zustandig und arbeiten mit dem Team zusammen. "
        "Die Stelle ist mit einem Pensum von 80% ausgeschrieben."
    )
    assert written_in_german(texte)
    score, label = score_german(offer(description=texte))
    assert score <= 0.25
    assert "allemand" in label


# ------------------------------------------------------------------ missions
def test_missions_role_dans_le_titre():
    score, _label, off_domain = score_missions(
        offer(
            title="Chargee de communication 80-100%",
            description="Plan de communication, relations medias, reseaux sociaux.",
        )
    )
    assert score > 0.8
    assert off_domain is False


def test_missions_metier_hors_profil():
    score, label, off_domain = score_missions(
        offer(
            title="Technicien SAV chauffage",
            description="Vous avez le sens de la communication.",
        )
    )
    assert off_domain is True
    assert score < 0.1
    assert "hors profil" in label


def test_ecriture_inclusive_reconnue():
    for titre in ["Charge de communication", "Chargé·e de communication", "Chargé(e) de communication"]:
        score, _, _ = score_missions(offer(title=titre, description="communication"))
        assert score > 0.5, titre


# ------------------------------------------------------------------ synthese
def test_offre_ideale_proche_de_100(cfg):
    o = offer(
        title="Charge de communication et evenementiel 80-100%",
        description=(
            "Vous pilotez le plan de communication, redigez les communiques de "
            "presse, animez les reseaux sociaux et coordonnez le sponsoring des "
            "salons. 3 a 5 ans d'experience. Allemand un atout."
        ),
    )
    score_offer(o, cfg)
    assert o.score >= 90
    assert sum(o.score_detail.values()) >= 90


def test_agence_interim_signalee(cfg):
    o = offer(employer="Adecco Ressources Humaines", employer_category="")
    score_offer(o, cfg)
    assert o.raw["blocked_employer"] is True
    assert o.score_detail["employeur"] == 0.0


def test_somme_des_criteres_bornee(cfg):
    o = offer(description="communication marketing evenementiel sponsoring")
    score_offer(o, cfg)
    assert 0 <= o.score <= 100
    for critere, poids in cfg.weights.items():
        assert 0 <= o.score_detail[critere] <= poids


# ------------------------------------------------------------------ mots-cles
def test_trois_mots_cles_non_redondants():
    o = offer(
        description=(
            "Vous elaborez le plan de communication, gerez les relations medias "
            "et animez les reseaux sociaux de nos evenements."
        )
    )
    mots = extract_keywords(o)
    assert len(mots) == 3
    for i, mot in enumerate(mots):
        for autre in mots[i + 1 :]:
            assert mot not in autre and autre not in mot
