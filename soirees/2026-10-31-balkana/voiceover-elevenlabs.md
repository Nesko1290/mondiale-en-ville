# BALKANA · Balkan Nightmare — Texte voix-off ElevenLabs v3

Soirée : Balkana · Balkan Nightmare
Lieu : Uptown Geneva
Date : Samedi 31 octobre 2026, nuit d'Halloween
Phase : BOF (J-2), chaque version finit sur l'achat du billet.

Formaté pour Eleven v3 : audio tags entre crochets, MAJUSCULES pour l'emphase,
points de suspension pour les respirations. À coller tels quels, tags compris.
Les horaires ne sont pas dans les textes (non confirmés). Une fois connus, ajouter
la ligne optionnelle marquée `(+ horaires)`.

---

## Version principale (~45 s) — spot complet

[whispers] Genève... cette nuit... tu vas faire un cauchemar.

[slowly] Samedi 31 octobre. La nuit d'Halloween.

[pause]

[sinister] Les lumières s'éteignent à l'Uptown... et quelque chose remonte des Balkans.

[short pause]

[excited] BALKANA ! Balkan Nightmare !

[confident] Les trompettes qui hurlent. Les basses qui te prennent au ventre. Les refrains que toute la salle connaît par cœur... et que tu vas crier jusqu'au matin.

[mischievously] Ici, personne n'a peur du noir. On a peur de rater la soirée.

[pause]

[confident] Samedi 31 octobre. Uptown Geneva. (+ horaires : de [[HORAIRES]].)

[whispers] Les billets en ligne partent maintenant... [short pause] à la porte, ce sera plus cher. Et peut-être trop tard.

[laughs evilly] Balkana. [short pause] Fais de beaux cauchemars.

---

## Version courte (~20 s) — story / reel

[whispers] Samedi 31 octobre... la nuit d'Halloween...

[excited] BALKANA ! Balkan Nightmare, à l'Uptown Geneva !

[confident] Son balkan toute la nuit. Trompettes, basses, et une salle qui chante en chœur.

[short pause]

[mischievously] Le seul cauchemar... c'est de rester devant la porte.

[confident] Prends ton billet maintenant. Lien en bio.

---

## Version ultra-courte (~9 s) — hook / retargeting

[whispers] Il te reste deux nuits... avant le cauchemar.

[excited] Balkana ! Samedi 31 octobre. Uptown Geneva.

[confident] Billets en ligne. [short pause] MAINTENANT.

---

## Variante J-0 (~12 s) — "c'est ce soir", à diffuser le samedi

[whispers] C'est ce soir.

[excited] BALKANA ! Balkan Nightmare ! Uptown Geneva !

[confident] Dernières entrées en ligne... après, c'est à la porte. Et à la porte... [mischievously] on ne garantit rien.

---

## Variante MC de club (~40 s) — criée, style annonce sur la piste

[shouts] GENÈVE ! Samedi 31 octobre... la nuit d'Halloween... BALKANA débarque à l'Uptown !

[excited] Balkan Nightmare ! Le cauchemar le plus festif de l'année !

[confident] Les trompettes ! Les basses ! Les refrains que tout le monde connaît ! On ne fait pas les choses à moitié !

[short pause]

[whispers] Écoute bien... [mischievously] cette nuit, les monstres dansent le kolo.

[excited] Toute la diaspora, tous les amis, toute la ville. SAMEDI. À l'Uptown.

[pause]

[shouts] Balkana ! [confident] Billets en ligne, maintenant. [whispers] Après... c'est le cauchemar.

---

## Réglages ElevenLabs v3

- Modèle : Eleven v3, langue français. Tags en anglais (mieux compris par le modèle).
- Stability : "Creative" pour la version MC et la version principale (les tags d'ambiance horreur
  ont besoin de marge), "Natural" pour les versions courtes. Éviter "Robust", il aplatit les tags.
- Voix : une voix grave, rauque ou "storyteller" pour la principale (ambiance film d'horreur),
  une voix hype/énergique pour la MC.
- Tags utilisés : [whispers] [slowly] [sinister] [excited] [confident] [mischievously]
  [shouts] [laughs evilly] [pause] [short pause]. `[sinister]` et `[laughs evilly]` sont à tester :
  si v3 les lit à voix haute ou les ignore, remplacer par `[whispers]` et `[laughs]`.
- 3 à 4 prises par version, garder la meilleure.
- Ajouter en post-prod une nappe sonore : trompette balkanique (style brass band) qui part en
  distorsion + rire / porte qui grince sur l'intro.
- Phonétique si besoin : Balkana → "Balkâna", Uptown → "Eup-taoune", kolo → "kolo".
