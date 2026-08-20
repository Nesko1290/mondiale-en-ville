"""Sorties : CSV et tableau Markdown tries par score."""

from __future__ import annotations

import csv
import logging
from datetime import date
from pathlib import Path

from .models import JobOffer

log = logging.getLogger("jobwatch.report")

COLUMNS = [
    "score", "titre", "employeur", "lieu", "date_parution", "url",
    "mots_cles_lettre", "nouveau", "source", "taux", "detail_score",
]


def write_csv(offers: list[JobOffer], path: Path) -> Path:
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=COLUMNS, delimiter=";")
        writer.writeheader()
        for offer in offers:
            writer.writerow(offer.to_row())
    log.info("CSV ecrit : %s (%d lignes)", path, len(offers))
    return path


def _escape(text: str) -> str:
    return (text or "").replace("|", "\\|").replace("\n", " ").strip()


def _escape_url(url: str) -> str:
    """Un `|` dans une URL casserait la cellule du tableau Markdown."""
    return (url or "").replace("|", "%7C").replace(")", "%29").replace(" ", "%20")


def _table(offers: list[JobOffer]) -> list[str]:
    lines = [
        "| Score | Titre | Employeur | Lieu | Parution | Mots-cles pour la lettre | Lien |",
        "|------:|-------|-----------|------|----------|--------------------------|------|",
    ]
    for offer in offers:
        row = offer.to_row()
        flag = " 🆕" if offer.is_new else ""
        lines.append(
            "| {score} | {titre}{flag} | {employeur} | {lieu} | {parution} | {kw} | [annonce]({url}) |".format(
                score=row["score"],
                titre=_escape(row["titre"]),
                flag=flag,
                employeur=_escape(row["employeur"]),
                lieu=_escape(row["lieu"]) or "-",
                parution=row["date_parution"] or "-",
                kw=_escape(row["mots_cles_lettre"]) or "-",
                url=_escape_url(row["url"]),
            )
        )
    return lines


def write_markdown(
    offers: list[JobOffer],
    path: Path,
    stats: dict[str, int] | None = None,
) -> Path:
    today = date.today().isoformat()
    new_offers = [o for o in offers if o.is_new]

    total = (stats or {}).get("retenues", len(offers))
    lines = [
        f"# Veille emploi communication / marketing / evenementiel — {today}",
        "",
        f"**{len(new_offers)} nouvelle(s) offre(s)** sur {total} annonce(s) "
        "au-dessus du seuil de score.",
        "",
    ]
    if stats:
        lines += [
            "<sub>"
            + " · ".join(f"{k} : {v}" for k, v in stats.items())
            + "</sub>",
            "",
        ]

    if new_offers:
        lines += ["## Nouveautes", ""] + _table(new_offers) + [""]
    else:
        lines += ["## Nouveautes", "", "_Aucune nouvelle offre depuis la derniere execution._", ""]

    known = [o for o in offers if not o.is_new]
    if known:
        lines += [
            "## Deja vues (toujours en ligne)",
            "",
            "<details><summary>Afficher</summary>",
            "",
        ] + _table(known) + ["", "</details>", ""]

    lines += [
        "---",
        "",
        "### Detail du score",
        "",
        "| Critere | Points |",
        "|---------|-------:|",
        "| Correspondance des missions | 40 |",
        "| Niveau d'experience demande (1-5 ans) | 20 |",
        "| Exigence d'allemand (penalisante au-dela de B2) | 15 |",
        "| Localisation (arc lemanique) | 15 |",
        "| Taille et type d'employeur | 10 |",
        "",
    ]
    if offers:
        lines += ["### Detail par offre", ""]
        for offer in offers[:20]:
            labels = offer.raw.get("score_labels", {})
            detail = ", ".join(f"{k} {v:g}" for k, v in offer.score_detail.items())
            lines.append(
                f"- **{offer.score}** — {offer.title} ({offer.employer}) : {detail}"
            )
            if labels:
                lines.append(
                    "  <br><sub>"
                    + " · ".join(f"{k} : {v}" for k, v in labels.items())
                    + "</sub>"
                )
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")
    log.info("Markdown ecrit : %s", path)
    return path
