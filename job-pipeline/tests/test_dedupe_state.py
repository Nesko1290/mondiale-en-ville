"""Tests de deduplication, du fichier d'etat et du parseur robots.txt."""

from datetime import date, timedelta
from pathlib import Path

from jobwatch.dedupe import deduplicate
from jobwatch.models import JobOffer, title_key
from jobwatch.robots import RobotsRules
from jobwatch.state import SeenState

TODAY = date(2026, 8, 20)


def offer(title, employer="Palexpo", published=TODAY, source="job-room", description=""):
    return JobOffer(
        title=title, employer=employer, url=f"https://exemple.ch/{title}",
        source=source, published=published, description=description,
    )


# ------------------------------------------------------------------- dedupe
def test_meme_titre_employeur_date_est_un_doublon():
    offers = [offer("Charge de communication"), offer("Charge de communication")]
    assert len(deduplicate(offers)) == 1


def test_titres_quasi_identiques_fusionnes():
    offers = [
        offer("Chargé·e de communication 80-100%"),
        offer("Chargée de communication", source="web:Palexpo",
              description="description complete de l'annonce"),
    ]
    kept = deduplicate(offers)
    assert len(kept) == 1
    # La version issue du site de l'employeur est preferee a celle de l'agregateur.
    assert kept[0].source == "web:Palexpo"
    assert kept[0].description


def test_employeurs_differents_ne_fusionnent_pas():
    offers = [offer("Charge de communication"), offer("Charge de communication", employer="Beaulieu")]
    assert len(deduplicate(offers)) == 2


def test_meme_poste_republie_plus_tard_reste_un_doublon():
    offers = [
        offer("Charge de communication", published=TODAY),
        offer("Charge de communication", published=TODAY - timedelta(days=10)),
    ]
    assert len(deduplicate(offers)) == 1


def test_republication_tres_ancienne_est_une_offre_distincte():
    offers = [
        offer("Charge de communication", published=TODAY),
        offer("Charge de communication", published=TODAY - timedelta(days=200)),
    ]
    assert len(deduplicate(offers)) == 2


def test_cle_de_titre_ignore_taux_et_genre():
    assert title_key("Charge de communication 80-100% (H/F) CDI") == title_key(
        "Charge de communication"
    )


# -------------------------------------------------------------------- etat
def test_premiere_execution_tout_est_nouveau(tmp_path: Path):
    state = SeenState(tmp_path / "seen.json")
    offers = [offer("Charge de communication"), offer("Event manager")]
    state.mark(offers)
    assert all(o.is_new for o in offers)
    state.save()
    assert (tmp_path / "seen.json").exists()


def test_deuxieme_execution_ne_signale_que_les_nouveautes(tmp_path: Path):
    path = tmp_path / "seen.json"
    SeenState(path).mark([offer("Charge de communication")])
    first = SeenState(path)
    first.mark([offer("Charge de communication")])
    first.save()

    second = SeenState(path)
    offers = [offer("Charge de communication"), offer("Brand manager")]
    second.mark(offers)
    assert offers[0].is_new is False
    assert offers[1].is_new is True


def test_purge_des_entrees_anciennes(tmp_path: Path):
    path = tmp_path / "seen.json"
    state = SeenState(path)
    state.entries = {
        "vieille": {"first_seen": "2020-01-01", "last_seen": "2020-01-01"},
        "recente": {"first_seen": TODAY.isoformat(), "last_seen": date.today().isoformat()},
    }
    assert state.purge(90) == 1
    assert "recente" in state.entries


def test_etat_corrompu_ne_fait_pas_planter(tmp_path: Path):
    path = tmp_path / "seen.json"
    path.write_text("{ ceci n'est pas du json", encoding="utf-8")
    assert SeenState(path).entries == {}


# ------------------------------------------------------------------ robots
def test_regle_la_plus_longue_gagne():
    rules = RobotsRules.parse("User-agent: *\nAllow: /\nDisallow: /suche/\n", "JobWatchBot/1.0")
    assert rules.can_fetch("https://x.ch/careers/") is True
    assert rules.can_fetch("https://x.ch/suche/abc") is False


def test_disallow_vide_autorise_tout():
    rules = RobotsRules.parse("User-agent: *\nDisallow:\n", "JobWatchBot/1.0")
    assert rules.can_fetch("https://x.ch/n-importe-quoi") is True


def test_groupe_specifique_prioritaire_sur_etoile():
    txt = "User-agent: JobWatchBot\nDisallow: /prive\nUser-agent: *\nDisallow: /\n"
    rules = RobotsRules.parse(txt, "JobWatchBot/1.0")
    assert rules.can_fetch("https://x.ch/public") is True
    assert rules.can_fetch("https://x.ch/prive/page") is False


def test_crawl_delay_lu():
    rules = RobotsRules.parse("User-agent: *\nCrawl-delay: 10\n", "JobWatchBot/1.0")
    assert rules.crawl_delay == 10.0


def test_joker_dans_le_motif():
    rules = RobotsRules.parse("User-agent: *\nDisallow: /*/prive\n", "JobWatchBot/1.0")
    assert rules.can_fetch("https://x.ch/fr/prive/page") is False
    assert rules.can_fetch("https://x.ch/fr/public") is True


# -------------------------------------------------- agregateurs (jobup, ...)
AGGREGATORS = ["jobup", "jobs.ch"]


def test_annonce_d_agregateur_fusionnee_avec_le_vrai_employeur():
    offers = [
        offer("Brand Manager à 80-100%", employer="Alloboissons SA"),
        offer("Brand Manager à 80-100%", employer="Jobup"),
    ]
    kept = deduplicate(offers, AGGREGATORS)
    assert len(kept) == 1
    assert kept[0].employer == "Alloboissons SA"


def test_annonce_d_agregateur_conservee_si_elle_est_seule():
    kept = deduplicate([offer("Coordinateur associatif", employer="Jobup")], AGGREGATORS)
    assert len(kept) == 1
    assert kept[0].employer == "Jobup"


def test_deux_employeurs_reels_ne_fusionnent_pas_via_l_agregateur():
    offers = [
        offer("Social Media Manager", employer="Nestle SA"),
        offer("Social Media Manager", employer="Logitech SA"),
    ]
    assert len(deduplicate(offers, AGGREGATORS)) == 2
