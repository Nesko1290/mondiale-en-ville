# BALKANA · Balkan Nightmare — Flyer tabloïd (kie.ai)

Concept : la soirée en **une de journal à scandale**, édition spéciale Halloween.
Un tabloïd fictif, "LE CAUCHEMAR BALKAN", daté du samedi 31 octobre 2026, qui "révèle"
qu'une nuit balkanique va hanter l'Uptown Geneva. Rouge/noir/blanc, typo condensée énorme,
photo flash façon paparazzi, grain d'impression papier journal.

Pourquoi ça marche en BOF : le format "ALERTE / DERNIÈRE MINUTE" porte naturellement l'urgence,
et il arrête le scroll (on lit une une de journal même quand on ignore une pub).

À remplir avant génération : `[[HORAIRES]]` (sinon retirer le bloc), `[[PRIX]]` (idem).

---

## Réglages kie.ai

- Image avec texte lisible : GPT Image (4o), Nano Banana, Seedream ou Ideogram. Tester 2 modèles
  et garder celui qui écrit le mieux.
- Retouche d'un rendu presque parfait (une lettre cassée, couleur) : Flux Kontext en mode édition.
- Formats : **4:5** pour le feed (1080×1350), **9:16** pour la story (1080×1920).
- Générer 4 images par prompt, vérifier l'orthographe de chaque bloc de texte.
- Si le texte sort mal après 3 essais : utiliser le prompt "fond seul" et poser le texte dans Canva / Adobe Express.

---

## Prompt principal — feed 4:5

```
A sensational European tabloid newspaper front page, Halloween special edition, printed on cheap newsprint with visible paper grain, halftone dots and slight ink bleed. Bold red masthead at the top with the newspaper name in white condensed letters: "LE CAUCHEMAR BALKAN". A yellow diagonal banner in the top corner reading "EXCLUSIF". Huge black ultra-condensed headline taking half the page: "ILS ARRIVENT SAMEDI". Main photo: a flash-lit paparazzi-style shot of a packed nightclub at night, crowd with arms raised, a Balkan brass trumpet player in a dark suit with a skull face paint in the foreground, red and purple stage lights, fog, slightly blurry motion, dramatic and fun rather than gory. Under the photo a white subheadline box: "BALKANA · BALKAN NIGHTMARE". Bottom strip in red with white text: "SAM. 31 OCT. · UPTOWN GENEVA". Small barcode in the bottom right corner. Classic tabloid layout, red, black, white and a touch of yellow, high contrast, ultra-legible typography, no other text.
```

**Negative prompt** (si le modèle l'accepte) :
```
gore, blood, real violence, misspelled text, extra text, gibberish letters, watermark, logo of real newspapers, distorted faces, extra fingers
```

---

## Variantes de gros titre (remplacer `"ILS ARRIVENT SAMEDI"`)

1. `"GENÈVE SOUS LE CHOC"` + sous-titre `"UNE NUIT BALKAN HANTE L'UPTOWN"`
2. `"PLUS QUE 48H"` (version urgence, à utiliser jeudi/vendredi)
3. `"C'EST CE SOIR"` (version J-0, samedi)
4. `"LA FILE D'ATTENTE TERRIFIE LES GENEVOIS"` + encadré `"PRENEZ VOS BILLETS EN LIGNE"` (lève l'objection file/porte)

Garder une seule variante par image : plus de 5 blocs de texte = lettres déformées.

---

## Prompt story — 9:16

```
Vertical 9:16 tabloid newspaper front page, Halloween special edition, cheap newsprint texture, halftone print, ink bleed. Red masthead at the top: "LE CAUCHEMAR BALKAN". Giant black condensed headline in the upper half: "PLUS QUE 48H". Center: flash paparazzi photo of a crowded dark nightclub with a skull-painted Balkan trumpet player blowing into his trumpet, red and purple lights, smoke. Lower third: white box with "BALKANA · BALKAN NIGHTMARE", then a red strip with "SAM. 31 OCT. · UPTOWN GENEVA". Leave the bottom 15% of the image as a plain dark red area with no text (space for the Instagram link sticker). Tabloid style, high contrast, legible typography, no other text.
```

---

## Prompt fond seul (sans texte, pour finir dans Canva / Express)

```
Tabloid newspaper front page layout with empty text areas, Halloween special edition, newsprint texture, halftone dots, red masthead block left blank, large empty headline space, central flash-lit paparazzi photo of a packed dark nightclub with a skull face-painted Balkan brass trumpet player, red and purple lights, fog, red bottom strip left blank. No text, no letters, no logos.
```

Texte à poser ensuite : masthead `LE CAUCHEMAR BALKAN` · titre `ILS ARRIVENT SAMEDI` ·
`BALKANA · BALKAN NIGHTMARE` · `SAM. 31 OCT. · UPTOWN GENEVA` · option `[[HORAIRES]]` · option `EN LIGNE [[PRIX]]`.
Typo conseillée : Anton / Bebas Neue / Oswald Bold (titres), Roboto Condensed (corps).

---

## Prompt vidéo teaser — 9:16, 5-8 s (Veo / Kling / Runway sur kie.ai)

À partir de l'image story générée (image-to-video) :

```
The tabloid newspaper front page lies on a wet dark street at night. Wind lifts the paper slightly, camera slowly pushes in on the headline. The paparazzi photo on the page comes alive: the skull-painted trumpet player starts blowing his trumpet, red and purple club lights flicker, fog rolls out of the photo onto the street. A camera flash goes off at the end. Cinematic, moody, Halloween atmosphere, no gore. Keep all printed text unchanged and legible.
```

Son : poser la version ultra-courte (~9 s) de la voix-off ElevenLabs par-dessus + trompette balkanique.

---

## Checklist rendu

- [ ] "BALKANA", "BALKAN NIGHTMARE", "UPTOWN GENEVA", "31 OCT." correctement écrits.
- [ ] Aucun logo ou nom de vrai journal.
- [ ] Pas de gore (refus Meta probable + hors ton).
- [ ] Zone safe en bas de la story pour le sticker lien.
- [ ] Même gros titre que l'ad qu'il accompagne (C → "PLUS QUE 48H", J-0 → "C'EST CE SOIR").
