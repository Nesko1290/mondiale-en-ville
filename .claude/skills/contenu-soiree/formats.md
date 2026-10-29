# Règles par format

## Voix-off ElevenLabs v3

- Modèle Eleven v3, langue français. Audio tags en anglais entre crochets droits suivis d'un espace :
  `[whispers] [confident] [excited] [mischievously] [shouts] [pause] [short pause]`,
  à tester : `[laughs] [sighs] [breathes]`. Pour un thème horreur : `[whispers]`, `[sinister]`, `[slowly]`, `[laughs evilly]`.
- MAJUSCULES = accent tonique, "..." = micro-pause. Pas plus d'une emphase par phrase.
- Structure : hook chuchoté → infos (nom, date, lieu, heures) → gimmick → montée → répétition des infos → signature.
- Version BOF : finir sur l'action ("Billets en ligne, maintenant. À la porte, ce sera plus cher.").
- Stability : "Creative" pour la version MC, "Natural" pour le reste, éviter "Robust".
- 3 à 4 prises par version (v3 non déterministe). Écrire phonétiquement les mots étrangers mal prononcés.

## Meta Ads (Facebook / Instagram)

- Texte principal : hook dans les 125 premiers caractères.
- Titre ≤ 40 caractères, description ≤ 30 caractères.
- CTA : "Obtenir des billets" (par défaut), "Réserver" (tables), "Envoyer un message" (WhatsApp VIP).
- 4 variantes : A hook gimmick, B hype, C urgence courte (retargeting), D question.
- En BOF : C devient la variante principale, budget concentré sur retargeting
  (visiteurs billetterie 7 j, engagés IG/FB 30 j, vidéo vue 50 %) + lookalike acheteurs.
- Ciblage par défaut : Genève + 40 km (Lausanne, Nyon, Annemasse, Haute-Savoie), 18-34 ans,
  intérêts liés aux styles musicaux et aux artistes de référence, langues pertinentes pour la communauté visée.
- Toujours un plan de diffusion jour par jour jusqu'à la soirée.

## Flyer tabloïd (kie.ai)

Concept : la soirée traitée comme la **une d'un journal à scandale** (style Blick / The Sun / Le Matin) :
gros titre choc en capitales, bandeau "EXCLUSIF" / "ALERTE", photo principale dramatique,
encadrés, sous-titres sensationnalistes, prix barré "comme en kiosque", code-barres, date d'édition = date de la soirée.

- Plateforme kie.ai (API agrégatrice). Choisir un modèle qui rend bien le texte dans l'image :
  GPT-4o Image / GPT Image, Nano Banana (Gemini), Seedream, Ideogram. Flux Kontext pour retoucher un visuel existant.
- Formats : feed 4:5 (1080×1350), story 9:16 (1080×1920). Vidéo teaser : Veo / Kling / Runway en 9:16, 5-8 s.
- Prompt en anglais pour la scène, **texte à afficher entre guillemets en français**, exact, court.
  Pas plus de 5 blocs de texte, sinon les modèles déforment les lettres.
- Toujours prévoir une version "sans texte" (fond seul) à finir dans Canva/Express si le texte sort mal.
- Livrer : 1 prompt principal + 2 variantes de gros titre + prompt story + prompt vidéo + negative prompt.
- Vérifier sur chaque rendu : orthographe, date, lieu. Re-générer plutôt que corriger à la main si une lettre est cassée.

## WhatsApp / SMS broadcast

- ≤ 300 caractères, 1re ligne = info qui fait ouvrir, 1 lien, 1-2 emojis.
- Pas d'accents encodés dans les liens `wa.me` pré-remplis (cf. commit 27379f6).
- Séquence BOF : J-2 annonce urgence, J-1 dernier palier, J-0 "ce soir", J-0 22h "dernières entrées en ligne".

## Stories Instagram

- 3 à 5 écrans par jour, texte ≤ 8 mots par écran.
- Stickers : compte à rebours, lien billetterie, sondage ou quiz (engagement → audience retargeting).

## Reels / TikTok

- Hook visuel + texte à l'écran dans les 1,5 premières secondes.
- 7 à 15 s, son tendance ou extrait d'un titre du style de la soirée.
- Texte final : nom · date · lieu · "lien en bio".

## Post organique

- Caption : hook, 3 lignes d'infos, CTA, hashtags (8-12) en fin de caption, jamais dans les ads.
