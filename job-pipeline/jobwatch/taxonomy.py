"""Vocabulaire metier : familles de missions, roles cibles, bruit a ecarter.

Tous les motifs sont ecrits en minuscules et sans accents : ils sont compares
au texte passe par `models.normalize()`.
"""

from __future__ import annotations

# Roles qui correspondent directement au profil. Un titre qui contient l'un
# d'eux vaut presque la totalite des points "missions".
CORE_ROLES: dict[str, float] = {
    "charge de communication": 1.0,
    "chargee de communication": 1.0,
    "charge de la communication": 1.0,
    "responsable communication": 1.0,
    "responsable de la communication": 1.0,
    "communication manager": 1.0,
    "communications manager": 1.0,
    "charge de marketing": 1.0,
    "responsable marketing": 1.0,
    "marketing manager": 1.0,
    "chef de produit marketing": 0.9,
    "brand manager": 1.0,
    "responsable de marque": 1.0,
    "charge de projet evenementiel": 1.0,
    "chef de projet evenementiel": 1.0,
    "event manager": 1.0,
    "responsable evenementiel": 1.0,
    "coordinateur evenementiel": 0.95,
    "coordinatrice evenementiel": 0.95,
    "charge de projet evenements": 0.95,
    "attache de presse": 1.0,
    "relations publiques": 0.95,
    "relations medias": 0.95,
    "public relations": 0.95,
    "pr manager": 0.95,
    "charge de partenariats": 0.95,
    "responsable partenariats": 0.95,
    "sponsoring manager": 0.95,
    "responsable sponsoring": 0.95,
    "community manager": 0.9,
    "social media manager": 0.9,
    "content manager": 0.9,
    "responsable contenu": 0.85,
    "charge de projet communication": 1.0,
    "chef de projet communication": 1.0,
    "assistant communication": 0.7,
    "assistante communication": 0.7,
    "assistant marketing": 0.7,
    "coordinateur communication": 0.95,
    "coordinatrice communication": 0.95,
    "marketing communication": 0.9,
    "communication interne": 0.9,
    "charge de communication digitale": 1.0,
    "digital marketing": 0.85,
    "marketing digital": 0.85,
    "responsable promotion": 0.8,
    "charge de projet culturel": 0.75,
    "mediation culturelle": 0.7,
}

# Familles thematiques : chaque famille apporte des points quand elle est
# presente dans le corps de l'annonce.
FAMILIES: dict[str, tuple[float, tuple[str, ...]]] = {
    "communication": (
        1.0,
        (
            "communication", "communiquer", "redaction", "redactionnel",
            "storytelling", "contenu", "contenus", "newsletter", "porte parole",
            "supports de communication", "plan de communication", "editorial",
            "communique", "interne et externe", "kommunikation",
        ),
    ),
    "marketing": (
        1.0,
        (
            "marketing", "campagne", "campagnes", "promotion", "acquisition",
            "crm", "notoriete", "positionnement", "etude de marche", "seo",
            "sea", "google analytics", "e mailing", "emailing", "growth",
            "strategie marketing", "plan marketing",
        ),
    ),
    "evenementiel": (
        1.0,
        (
            "evenementiel", "evenement", "evenements", "salon", "salons",
            "congres", "exposition", "expositions", "foire", "manifestation",
            "manifestations", "exposant", "exposants", "inauguration",
            "conference", "conferences", "protocole", "scenographie",
            "logistique evenementielle", "event", "events", "veranstaltung",
        ),
    ),
    "brand_rp": (
        1.0,
        (
            "brand", "marque", "marques", "image de marque", "identite visuelle",
            "relations publiques", "relations presse", "relations medias",
            "presse", "medias", "rp", "public relations", "reputation",
            "influence", "influenceurs", "porte parole", "branding",
        ),
    ),
    "sponsoring": (
        0.9,
        (
            "sponsoring", "sponsors", "sponsor", "partenariat", "partenariats",
            "mecenat", "fundraising", "levee de fonds", "donateurs",
            "partenaires", "sponsorship",
        ),
    ),
    "digital": (
        0.7,
        (
            "reseaux sociaux", "social media", "linkedin", "instagram",
            "site internet", "site web", "cms", "wordpress", "community",
            "digital", "numerique", "webmarketing", "podcast", "video",
        ),
    ),
    "outils": (
        0.5,
        (
            "indesign", "photoshop", "illustrator", "canva", "suite adobe",
            "mailchimp", "hubspot", "salesforce", "graphisme", "print",
            "charte graphique", "powerpoint",
        ),
    ),
}

# Metiers hors profil : si le titre en releve, l'annonce est ecartee meme
# quand "communication" apparait dans les qualites demandees.
OFF_DOMAIN_TITLE = (
    "developpeur", "developpeuse", "software", "ingenieur", "ingenieure",
    "technicien", "technicienne", "electricien", "mecanicien", "polymecanicien",
    "infirmier", "infirmiere", "medecin", "aide soignant", "soignante",
    "comptable", "fiduciaire", "audit", "auditeur", "juriste", "avocat",
    "notaire", "vendeur", "vendeuse", "caissier", "serveur", "serveuse",
    "cuisinier", "chef de cuisine", "sommelier", "chauffeur", "livreur",
    "magasinier", "logisticien", "conducteur", "menuisier", "peintre",
    "macon", "plombier", "sanitaire", "chauffagiste", "ferblantier",
    "nettoyage", "concierge", "agent de securite", "securite incendie",
    "enseignant", "professeur", "educateur", "educatrice", "assistant social",
    "data scientist", "data engineer", "devops", "administrateur systeme",
    "architecte logiciel", "analyste financier", "gestionnaire de fortune",
    "conseiller clientele", "conseillere clientele", "assurance",
    "pharmacien", "laborantin", "biologiste", "chimiste", "apprenti",
    "apprentie", "stagiaire hotellerie", "receptionniste", "gouvernante",
    "coiffeur", "estheticienne", "opticien", "boulanger", "boucher",
    "horloger", "horlogere", "sertisseur", "polisseur", "emailleur",
    "hauswirtschaft", "reinigung", "hausdienst", "haustechnik", "pflege",
    "buchhalter", "treuhand", "entwickler", "verkaufer", "verkauferin",
    "koch", "kochin", "servicemitarbeiter", "lagerist", "monteur",
    "intendance", "lingerie", "econome", "jardinier", "huissier",
    "aide de cuisine", "employe de maison", "femme de chambre",
    "bibliothecaire", "documentaliste", "archiviste", "etablissement scolaire",
    "legal director", "legal counsel", "compliance", "risk manager",
    "business analyst", "product owner", "scrum", "acheteur", "approvisionnement",
)

# Mots vides pour l'extraction des mots-cles de lettre de motivation.
STOPWORDS = set(
    """
    a au aux avec ce ces dans de des du elle en et eux il je la le les leur lui
    ma mais me meme mes moi mon ne nos notre nous on ou par pas pour qu que qui
    sa se ses son sur ta te tes toi ton tu un une vos votre vous c d j l m n s t
    y ete etee etees etes etant suis es est sommes etes sont serai seras sera
    serons serez seront etais etait etions etiez etaient fus fut fumes futes
    furent ai as avons avez ont aurai auras aura aurons aurez auront avais avait
    avions aviez avaient eus eut eumes eutes eurent aie aies ait ayons ayez aient
    the and for with you your our their they that this from will are was were
    have has had not but all any can our als der die das und mit fur von den dem
    ein eine ist sind wir sie ihre ihr auch bei nach als aus dass
    poste postes profil profils mission missions tache taches nous vous offre
    offrons cherchons recherchons recherche rejoindre rejoignez candidature
    dossier entreprise societe equipe equipes travail emploi place ans annee
    annees experience competences connaissance connaissances maitrise excellent
    excellente bonne bon tres plus moins entre autres notamment ainsi afin
    aupres selon dont sous chez lors cadre sein type contrat duree indeterminee
    determinee taux activite temps partiel plein salaire debut immediat suite
    idealement souhaite souhaitee requis requise demande demandee capacite sens
    esprit gout forte fort grande grand nouvelle nouveau nouveaux
    """.split()
)
