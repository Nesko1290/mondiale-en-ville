# Veille emploi — communication / marketing / événementiel, Suisse romande

Pipeline Python qui agrège chaque matin les offres pertinentes pour un profil
**communication / marketing / événementiel, 4 ans d'expérience, français langue
maternelle, anglais C1, allemand B1**, sur les cantons **GE, VD, VS, FR, NE**.

Il interroge l'API publique **job-room.ch** (SECO / Travail.swiss), visite les
pages carrière et flux RSS d'une liste d'employeurs cibles, déduplique, note
chaque offre de 0 à 100, et ne signale que les nouveautés d'une exécution à
l'autre.

---

## Installation

```bash
cd job-pipeline
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Utilisation

```bash
python -m jobwatch run                      # veille complète
python -m jobwatch run --only-new           # seulement les offres jamais vues
python -m jobwatch run --source Palexpo     # tester un employeur isolément
python -m jobwatch sources                  # lister les sources configurées
python -m jobwatch discover https://www.exemple.ch   # trouver une page carrière
python -m jobwatch state                    # ce que le pipeline a déjà vu
python -m jobwatch state --reset            # tout re-signaler comme nouveau
python -m pytest tests/ -q                  # 48 tests, sans accès réseau
```

Sorties dans `out/` :

| Fichier | Contenu |
|---|---|
| `offres_AAAA-MM-JJ.csv` | toutes les offres retenues, `;` comme séparateur (Excel FR) |
| `offres_AAAA-MM-JJ.md` | tableau Markdown trié par score, nouveautés en tête |
| `latest.md` | copie du dernier rapport, pratique à ouvrir depuis un raccourci |
| `nouveautes_*.csv/.md` | générés à la place des précédents avec `--only-new` |

`exemples/` contient la sortie d'une exécution réelle du 20.08.2026
(579 annonces collectées → 508 après déduplication → 48 retenues) : de quoi
voir à quoi ressemble le résultat avant de lancer quoi que ce soit.

Colonnes du CSV : `score`, `titre`, `employeur`, `lieu`, `date_parution`, `url`,
`mots_cles_lettre` (les trois mots-clés de l'annonce à reprendre dans la lettre),
`nouveau`, `source`, `taux`, `detail_score`.

---

## Les six étapes

### 1. API job-room.ch (SECO)

`POST https://api.job-room.ch/jobadservice/api/jobAdvertisements/_search`,
sans clé ni authentification. Une requête par mot-clé
(*communication, marketing, événementiel, chargé de communication, brand,
relations publiques, sponsoring*), filtrée sur `cantonCodes: [GE, VD, VS, FR, NE]`,
paginée via l'en-tête `X-Total-Count`.

La recherche ne renvoie qu'un extrait de l'annonce (avec les termes trouvés
entourés de `<em>`). Le pipeline appelle donc
`GET /jobAdvertisements/{id}` pour récupérer le texte intégral — indispensable
au scoring — mais **seulement** sur les annonces dont le titre passe un
pré-filtre de pertinence, pour ne pas marteler l'API (`max_details` dans
`config.yaml`).

### 2. Employeurs cibles

Trois types de sources, déclarés dans `config.yaml` :

```yaml
- name: Palexpo
  location: "Genève"
  canton: GE
  category: evenementiel
  sources:
    - type: career                      # page carrière HTML
      url: "https://www.palexpo.ch/carrieres/"
      # selector: ".job-list a"         # optionnel, si l'heuristique se trompe
```

* `career` — page carrière HTML. Plutôt qu'un parseur par site, l'extracteur
  repère les liens qui *ressemblent* à des annonces (URL contenant
  `emploi`/`job`/`stelle`…, intitulé de poste plausible, taux d'activité,
  mention `(H/F)`), puis ouvre chaque annonce pour en lire le texte et la date.
  Menu, en-tête et pied de page sont retirés avant analyse — sinon le
  « Suivez nos **événements** » du pied de page fausserait le score. Les données
  `schema.org/JobPosting` sont utilisées en priorité quand le site en publie, et
  les formulations du type « aucun poste ouvert » sont reconnues.
* `rss` — flux RSS/Atom.
* `ats` — API publique d'une plateforme de recrutement (`greenhouse`, `lever`,
  `smartrecruiters`, `recruitee`, `personio`). **À privilégier** quand
  l'employeur en utilise une : le JSON est stable là où une page carrière casse.

**Pour ajouter vos employeurs** (Palexpo, Genève Tourisme, organisateurs de
salons, horlogerie, études d'avocats, institutions culturelles) :

```bash
python -m jobwatch discover https://www.employeur.ch
```

La commande liste les liens « carrière / emploi / jobs » et les flux RSS du
site ; il n'y a plus qu'à copier l'URL dans `config.yaml`. La liste livrée est
un point de départ vérifié — remplacez-la par la vôtre.

### Politesse

* `User-Agent` identifiable avec adresse de contact, dans `config.yaml`.
* **2 secondes** entre deux requêtes vers un même hôte (délai appliqué *par
  hôte* : deux sites différents ne s'attendent pas). L'API job-room, prévue
  pour l'accès automatisé, utilise un délai plus court (`api_delay_seconds`).
* `robots.txt` respecté, avec la règle de précédence du **motif le plus long**
  (RFC 9309) — `urllib.robotparser` se trompe sur un `Allow: /` suivi d'un
  `Disallow: /suche/`, d'où le parseur maison dans `jobwatch/robots.py`. Un
  `Crawl-delay` plus long que le nôtre est appliqué.
* Réessais avec temporisation exponentielle (2 s, 4 s, 8 s) sur 429/5xx.
* Une source en panne est journalisée et ignorée : elle n'interrompt pas la veille.

### 3. Déduplication

Empreinte **titre + employeur + date de parution**, le titre étant d'abord
normalisé : accents, écriture inclusive (`Chargé·e` → `charge`), taux d'activité
(`80-100%`), mentions `(H/F)` et `CDI` sont neutralisés.

Deux rattrapages complètent la clé exacte :

* **titres proches** — même employeur, similarité ≥ 0,87, parution à moins de
  30 jours : la même annonce vue via job-room et via le site de l'employeur ne
  compte qu'une fois. La version du site de l'employeur est conservée (lien plus
  stable, texte complet), enrichie de ce que l'autre apportait.
* **agrégateurs** — une annonce republiée sous le nom de `jobup` est comparée
  aux offres de *tous* les employeurs, et fusionnée avec celle du vrai
  employeur quand il publie aussi de son côté (elle est conservée sinon).

### 4. Score sur 100

| Critère | Points | Méthode |
|---|---:|---|
| Correspondance des missions | 40 | ~50 intitulés de poste cibles + 7 familles thématiques (communication, marketing, événementiel, brand/RP, sponsoring, digital, outils). Le titre pèse 60 %, le corps 40 %. |
| Niveau d'expérience demandé | 20 | Extraction de « 3 à 5 ans », « au moins 5 ans », « 10 Jahre »… **uniquement** dans un contexte d'expérience. Plein score si le minimum demandé ≤ 5 ans ; dégressif au-delà. À défaut, lecture du titre (stage, junior, senior, direction). |
| Exigence d'allemand | 15 | Données structurées `languageSkills` de job-room **et** texte libre (« allemand C1 », « bonnes connaissances », « Muttersprache »). ≤ B1 : 15 pts ; « un atout » : 13,5 ; B2 : 10,5 ; C1 : 3,8 ; C2/maternelle : 0. Une annonce **rédigée entièrement en allemand** est traitée comme exigeant l'allemand, même sans mention explicite. |
| Localisation | 15 | Barème par commune (arc lémanique 1,0 ; Chablais/Riviera 0,85 ; Fribourg/Neuchâtel/Valais central 0,6 ; Suisse alémanique 0,3), repli sur le canton, puis sur une ville citée dans le texte, puis sur le télétravail. |
| Taille et type d'employeur | 10 | Catégorie déclarée dans `config.yaml` (événementiel, institution culturelle, horlogerie, étude d'avocats, secteur public…), déduite du nom sinon. |

Deux garde-fous, faute de quoi une annonce hors sujet remonte grâce au lieu et
à l'employeur :

* **métier hors profil** — un titre de technicien, comptable, infirmier,
  bibliothécaire… écarte l'annonce, même si « le sens de la communication »
  figure dans les qualités demandées ;
* **porte de pertinence** — sous 0,25 sur le critère « missions », le total est
  réduit proportionnellement ;
* les **agences de placement** (Adecco, Manpower, Michael Page…) sont écartées :
  elles republient en masse et masquent l'employeur réel.

Le seuil de publication est `filters.min_score` (45 par défaut).

Les **trois mots-clés** de chaque ligne sont les expressions métier les plus
saillantes réellement présentes dans l'annonce (pondérées par leur présence
dans le titre et par le poids de leur famille), sans redondance entre elles :
elles se reprennent telles quelles dans la lettre de motivation.

### 5. Sorties

CSV et Markdown triés par score décroissant. Le rapport Markdown sépare les
**nouveautés** (marquées 🆕) des offres déjà vues encore en ligne, repliées dans
un bloc dépliant, et détaille le score critère par critère pour les 20
premières — pratique pour comprendre pourquoi une offre est remontée ou non.

### 6. Fichier d'état

`state/seen.json` : empreinte → `{first_seen, last_seen, titre, employeur, url,
score}`. À chaque exécution, une offre déjà connue est marquée `nouveau = non`.
Écriture atomique (fichier temporaire puis `replace`), et purge automatique des
entrées plus vieilles que `output.keep_days` (90 jours) pour que le fichier ne
grossisse pas indéfiniment.

---

## Lancement quotidien

`run_daily.sh` crée l'environnement virtuel au premier appel, installe les
dépendances, puis lance la veille en journalisant dans `logs/`.

```bash
chmod +x run_daily.sh
./run_daily.sh --only-new
```

### cron (Linux, macOS)

```bash
crontab -e
```

```cron
# Veille emploi : chaque matin à 7h15
15 7 * * * /chemin/vers/job-pipeline/run_daily.sh --only-new >> /chemin/vers/job-pipeline/logs/cron.log 2>&1
```

`cron` démarre avec un environnement minimal : indiquez toujours le **chemin
absolu** du script. Il ne rattrape pas une exécution manquée (machine éteinte) —
préférez systemd ou launchd si c'est important.

### systemd (Linux, recommandé)

`jobwatch.service` et `jobwatch.timer` sont fournis.

```bash
mkdir -p ~/.config/systemd/user
cp jobwatch.service jobwatch.timer ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now jobwatch.timer

systemctl --user list-timers jobwatch     # prochaine exécution
journalctl --user -u jobwatch -n 50       # dernier journal
sudo loginctl enable-linger "$USER"       # lancer même sans session ouverte
```

`Persistent=true` rattrape l'exécution du matin si la machine était éteinte.

### launchd (macOS)

`ch.jobwatch.daily.plist` est fourni.

```bash
cp ch.jobwatch.daily.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/ch.jobwatch.daily.plist
launchctl list | grep jobwatch
```

launchd rattrape lui aussi une exécution manquée au réveil du Mac.

### Recevoir le résultat par e-mail

Le rapport est un fichier Markdown : une ligne suffit à se l'envoyer.

```bash
./run_daily.sh --only-new && \
  mail -s "Veille emploi $(date +%d.%m)" vous@exemple.ch < out/latest.md
```

---

## Réglages courants

| Envie | Où |
|---|---|
| Ajouter un employeur | `employers:` dans `config.yaml` (`python -m jobwatch discover` pour trouver l'URL) |
| Élargir/restreindre la zone | `jobroom.cantons` et `scoring.location_tiers` |
| Recevoir moins d'offres | augmenter `filters.min_score` |
| Changer l'importance d'un critère | `scoring.weights` (le total n'a pas à faire 100, il est utilisé tel quel) |
| Tolérer l'allemand | `profile.german_max_comfortable: C1` |
| Écarter un employeur récurrent | `scoring.blocklist_employers` |
| Explorer plus loin dans job-room | `jobroom.max_pages_per_keyword` et `max_details` |

## Limites connues

* Les pages carrière en JavaScript (Workday, Cornerstone, SuccessFactors…) ne
  rendent rien à un simple `GET`. Utilisez l'entrée `ats` si la plateforme
  expose une API publique, sinon l'employeur restera muet — le journal le dit.
* `jobup.ch` et `jobs.ch` n'ont pas d'API publique et leurs conditions
  d'utilisation interdisent l'extraction automatisée : ils ne sont pas
  interrogés. Une partie de leurs annonces remonte malgré tout via job-room,
  qui les rediffuse légitimement.
* Le score est une aide au tri, pas un verdict : parcourez aussi ce qui se
  situe juste sous le seuil les premières semaines, et ajustez les poids.
