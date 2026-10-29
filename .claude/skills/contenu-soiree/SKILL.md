---
name: contenu-soiree
description: Génère le pack de contenu marketing complet d'une soirée (voix-off ElevenLabs v3, textes Meta Ads orientés conversion/BOF, flyer tabloïd à générer sur kie.ai, stories, messages WhatsApp/SMS, scripts Reels/TikTok, posts organiques). À utiliser dès qu'on annonce une nouvelle soirée (lien FourVenues, nom + date + lieu) ou qu'on demande "la même chose" que pour une soirée précédente.
---

# Pack contenu soirée

Objectif : pour chaque soirée, livrer un pack prêt à coller, cohérent sur tous les formats,
et **orienté bas de funnel (BOF)** : faire passer le client de "je connais" à "j'ai mon billet".
Chaque contenu se termine sur une action (billet, réservation table, WhatsApp).

## 1. Collecter la fiche soirée

Remplir d'abord la fiche (voir `fiche-soiree-modele.md`) :
nom, sous-titre/thème, date, horaires, lieu + adresse, styles musicaux, DJs/artistes,
dress code, âge, tarifs et paliers (early / regular / last), tables/VIP, lien billetterie,
signature visuelle ou "gimmick" de la soirée (ex. La Cacita : une casita au milieu de la piste).

Sources, dans l'ordre :
1. Ce que l'utilisateur donne dans le message.
2. La page FourVenues. Elle est derrière une protection anti-bot Cloudflare :
   WebFetch, curl et Playwright headless renvoient tous 403 / "Just a moment".
   L'URL elle-même contient déjà nom, sous-titre, lieu et date
   (`/events/<nom>--<theme>--<lieu>--<jour-date>-<jj-mm-aaaa>-<id>`) : la parser.
3. Recherche web (Instagram, Resident Advisor, site du lieu).

**Ne jamais inventer** un DJ, un prix, un horaire ou un nombre de places restantes.
Ce qui n'est pas vérifié reste un placeholder visible `[[HORAIRES]]`, `[[DJS]]`, `[[PRIX]]`
et est listé en tête de chaque fichier dans "À compléter avant diffusion".

## 2. Déterminer la phase de funnel

Calculer J-x entre aujourd'hui et la soirée :

| Délai | Phase | Ton dominant |
|---|---|---|
| > J-14 | TOF / lancement | découverte, hype, le gimmick |
| J-14 à J-4 | MOF / considération | preuve sociale, line-up, paliers de prix |
| ≤ J-3 | **BOF / pressing** | urgence, rareté, dernier appel, objection levée |

Toujours livrer le pack BOF. Ajouter TOF/MOF seulement s'il reste plus de 4 jours.

Leviers BOF (en utiliser 2-3 par message, jamais tous) :
- Compte à rebours concret ("samedi", "dans 48h", "ce soir").
- Rareté vraie : palier qui ferme, prix qui monte à la porte. Pas de "sold out" inventé.
- FOMO social : "tout Genève sera là", "ta team a déjà pris".
- Lever l'objection : prix porte > prix en ligne, file d'attente, dress code, accès TPG.
- Une seule action, un seul lien.

## 3. Livrables

Créer `soirees/<aaaa-mm-jj>-<slug>/` avec :

| Fichier | Contenu |
|---|---|
| `fiche.md` | fiche soirée remplie + liste "À compléter" |
| `voiceover-elevenlabs.md` | 4 versions : ~45 s, ~20 s, ~9 s hook, variante MC ; + réglages v3 |
| `meta-ads.md` | 4 variantes (A hook, B hype, C urgence retargeting, D question), titres/descriptions A/B, texte story, ciblage, plan de diffusion BOF |
| `flyer-tabloid-kie.md` | concept "une de tabloïd" + prompts kie.ai (feed 4:5, story 9:16, teaser vidéo) |
| `autres-contenus.md` | WhatsApp/SMS broadcast, séquence stories J-2/J-1/J-0, scripts Reels/TikTok, post organique + hashtags, message tables/VIP, push "ce soir" |

Les règles de chaque format sont dans `formats.md` : les lire avant d'écrire.

## 4. Règles d'écriture

- Français, tutoiement, phrases courtes. Accents corrects dans les .md.
- Le gimmick / l'accroche dans les 125 premiers caractères des ads.
- Répéter les 3 infos clés partout : **nom · jour + date · lieu**.
- Pas de tiret cadratin dans les textes à coller (ads, voix-off, WhatsApp) : utiliser points, virgules, "·".
- Emojis : 1 à 3 par texte d'ad, aucun dans la voix-off.
- Exemple de référence (ton validé) : pack La Cacita, branche
  `claude/la-cacita-eleven-labs-text-xnyo9r` (`la-cacita-meta-ads.md`, `la-cacita-voiceover-elevenlabs.md`).

## 5. Finir

- Relire : aucune info inventée, placeholders listés, mêmes date/lieu dans tous les fichiers.
- Commit `<Nom soirée> : pack contenu (voix-off, ads, flyer tabloïd, autres)` et push.
- Dans la réponse : lien des fichiers, liste des placeholders à remplir, proposition de 1-2 formats en plus.
