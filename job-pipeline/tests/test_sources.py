"""Tests des connecteurs, sans acces reseau : le fetcher est simule."""

from datetime import date

from jobwatch.config import Employer, Source
from jobwatch.sources.careerpages import CareerPageSource
from jobwatch.sources.jobroom import _to_offer

PAGE_LISTE = """
<html><body>
<nav><a href="/fr/contact">Contact</a><a href="/fr/emploi">Emploi</a></nav>
<main>
  <h1>Nos offres d'emploi</h1>
  <ul>
    <li><a href="/carrieres/charge-de-communication">Chargé·e de communication 80-100%</a></li>
    <li><a href="/carrieres/technicien-lumiere">Technicien lumière (H/F)</a></li>
  </ul>
</main>
<footer><a href="/fr/newsletter">Newsletter</a></footer>
</body></html>
"""

PAGE_ANNONCE = """
<html lang="fr"><body><main>
  <h1>Chargé·e de communication</h1>
  <time datetime="2026-08-12">12.08.2026</time>
  <p>Vous pilotez le plan de communication et les relations medias de nos salons.
     3 a 5 ans d'experience. Lieu de travail : Genève.</p>
</main>
<footer>Suivez nos evenements sur les reseaux sociaux</footer></body></html>
"""

PAGE_VIDE = """
<html><body><main><h1>Emploi</h1>
<p>Le Grand Theatre n'a pas de poste ouvert en ce moment.</p>
<a href="/spectacles/carmen">Carmen</a></main></body></html>
"""


class FakeResponse:
    def __init__(self, text, url, status=200):
        self.text, self.url, self.status_code = text, url, status
        self.content = text.encode()


class FakeFetcher:
    """Rend une page differente selon l'URL demandee, et compte les appels."""

    def __init__(self, pages):
        self.pages = pages
        self.calls = []

    def get(self, url, **_kwargs):
        self.calls.append(url)
        for fragment, body in self.pages.items():
            if fragment in url:
                return FakeResponse(body, url)
        return FakeResponse("<html></html>", url, 404)


EMPLOYEUR = Employer(name="Palexpo", category="evenementiel", location="Geneve", canton="GE")
SOURCE = Source(type="career", url="https://exemple.ch/carrieres/")


def test_extraction_des_annonces_d_une_page_carriere():
    fetcher = FakeFetcher(
        {
            "carrieres/charge-de-communication": PAGE_ANNONCE,
            "carrieres/technicien-lumiere": PAGE_ANNONCE,
            "carrieres/": PAGE_LISTE,
        }
    )
    offers = CareerPageSource(EMPLOYEUR, SOURCE, fetcher).fetch()
    titres = [o.title for o in offers]
    assert "Chargé·e de communication 80-100%" in titres
    assert "Technicien lumière (H/F)" in titres
    # Ni le menu ni le pied de page ne doivent produire d'offres.
    assert not any("Newsletter" in t or "Contact" in t for t in titres)


def test_date_et_texte_recuperes_sur_la_page_de_l_annonce():
    fetcher = FakeFetcher(
        {"carrieres/charge-de-communication": PAGE_ANNONCE, "carrieres/": PAGE_LISTE}
    )
    offers = CareerPageSource(EMPLOYEUR, SOURCE, fetcher).fetch()
    offre = next(o for o in offers if "communication" in o.title)
    assert offre.published == date(2026, 8, 12)
    assert "plan de communication" in offre.description
    assert offre.workload == "80-100%"
    # Le pied de page est retire du texte analyse.
    assert "Suivez nos evenements" not in offre.description


def test_page_sans_offre_ne_produit_rien():
    fetcher = FakeFetcher({"carrieres/": PAGE_VIDE})
    assert CareerPageSource(EMPLOYEUR, SOURCE, fetcher).fetch() == []


def test_categorie_de_l_employeur_propagee():
    fetcher = FakeFetcher(
        {"carrieres/charge-de-communication": PAGE_ANNONCE, "carrieres/": PAGE_LISTE}
    )
    offers = CareerPageSource(EMPLOYEUR, SOURCE, fetcher).fetch()
    assert all(o.employer_category == "evenementiel" for o in offers)
    assert all(o.source == "web:Palexpo" for o in offers)


# ------------------------------------------------------------------ job-room
PAYLOAD = {
    "id": "abc-123",
    "jobContent": {
        "externalUrl": "",
        "jobDescriptions": [
            {"languageIsoCode": "de", "title": "Kommunikation", "description": "..."},
            {"languageIsoCode": "fr", "title": "Charge de communication",
             "description": "Plan de communication et relations medias."},
        ],
        "company": {"name": "Palexpo SA"},
        "employment": {"workloadPercentageMin": "80", "workloadPercentageMax": "100"},
        "location": {"city": "Geneve", "cantonCode": "GE"},
        "languageSkills": [{"languageIsoCode": "de", "spokenLevel": "GOOD"}],
    },
    "publication": {"startDate": "2026-08-15"},
}


def test_conversion_d_une_annonce_job_room():
    offre = _to_offer(PAYLOAD)
    assert offre is not None
    assert offre.title == "Charge de communication"     # version francaise choisie
    assert offre.employer == "Palexpo SA"
    assert offre.canton == "GE"
    assert offre.workload == "80-100%"
    assert offre.published == date(2026, 8, 15)
    assert offre.language_skills[0]["languageIsoCode"] == "de"
    # Sans lien externe, on retombe sur la fiche publique job-room.
    assert offre.url == "https://www.job-room.ch/job-search/abc-123"


def test_lien_externe_prefere_quand_il_existe():
    payload = {**PAYLOAD}
    payload["jobContent"] = {**PAYLOAD["jobContent"], "externalUrl": "https://jobs.ch/x"}
    assert _to_offer(payload).url == "https://jobs.ch/x"


def test_annonce_sans_titre_ignoree():
    payload = {"id": "x", "jobContent": {"jobDescriptions": []}, "publication": {}}
    assert _to_offer(payload) is None
