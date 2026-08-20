"""Tests des sorties CSV et Markdown."""

import csv
from datetime import date

from jobwatch.models import JobOffer
from jobwatch.report import write_csv, write_markdown


def offre(titre, score, is_new=True, url="https://exemple.ch/offre"):
    o = JobOffer(
        title=titre, employer="Palexpo | SA", url=url, source="web:test",
        location="Geneve", published=date(2026, 8, 19),
    )
    o.score = score
    o.is_new = is_new
    o.keywords = ["communication", "evenementiel", "sponsoring"]
    o.score_detail = {"missions": 40.0, "experience": 20.0}
    return o


def test_csv_contient_les_colonnes_demandees(tmp_path):
    path = write_csv([offre("Charge de communication", 90)], tmp_path / "o.csv")
    with path.open(encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh, delimiter=";"))
    assert len(rows) == 1
    ligne = rows[0]
    for colonne in ("titre", "employeur", "lieu", "date_parution", "score", "url",
                    "mots_cles_lettre"):
        assert ligne[colonne]
    assert ligne["mots_cles_lettre"] == "communication | evenementiel | sponsoring"
    assert ligne["date_parution"] == "2026-08-19"


def test_markdown_separe_nouveautes_et_deja_vues(tmp_path):
    offres = [offre("Nouvelle offre", 90), offre("Ancienne offre", 60, is_new=False)]
    texte = write_markdown(offres, tmp_path / "o.md", {"retenues": 2}).read_text(
        encoding="utf-8"
    )
    nouveautes, deja_vues = texte.split("## Deja vues")
    assert "Nouvelle offre" in nouveautes and "Ancienne offre" not in nouveautes
    assert "Ancienne offre" in deja_vues


def test_les_pipes_ne_cassent_pas_le_tableau(tmp_path):
    url = "https://exemple.ch/o?utm=wb:jobup|tg:b2c|cn:ch"
    texte = write_markdown([offre("Charge de communication", 90, url=url)],
                           tmp_path / "o.md").read_text(encoding="utf-8")
    ligne = next(l for l in texte.splitlines() if "Charge de communication" in l)
    # 7 colonnes => 8 barres verticales non echappees.
    assert ligne.count("|") - ligne.count("\\|") == 8
    assert "%7C" in ligne


def test_message_quand_rien_de_neuf(tmp_path):
    texte = write_markdown([], tmp_path / "o.md", {"retenues": 12}).read_text(
        encoding="utf-8"
    )
    assert "Aucune nouvelle offre" in texte
    assert "sur 12 annonce(s)" in texte
