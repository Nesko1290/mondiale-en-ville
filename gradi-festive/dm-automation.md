# GRADI FESTIF EXPÉRIENCE — Instagram DM Automation

Tool: **ManyChat Pro** (official Meta partner). Alternatives: Inro, CreatorFlow. Use only
official Meta API tools.

## ⚠️ "DM right after a follow": what's actually allowed

Instagram's official Messaging API **has no "new follower" trigger**. A business account can
only send automated DMs **after the person has interacted first** (sent a DM, replied to a
story, commented, tapped an ad's "Send message" button, clicked an ice breaker). Tools that
promise "auto-DM every new follower" run outside the API (they log in as you or scrape). That
is how accounts get **restricted or banned**, and losing the account three weeks before
opening is the worst outcome possible.

So we get the same effect in compliant ways:

1. **Make following the price of the gift ("follow-gate").** Every entry point (comment,
   story, ad) asks them to follow, and the flow checks it before sending the gift.
   Result: follow + DM conversation + lead, all in one move.
2. **Give every new visitor a reason to DM first.** The bio, the pinned posts and the highlights
   all say: *"Envoie FÊTE en DM 🎁"*. Ice breakers greet them the second they open the chat.
3. **Human welcome DM to new followers (manual, max ~30/day).** Every evening someone from the
   team opens the follower list and sends a short personal message (script below). It feels
   personal, it converts very well, and at this volume it's safe.

---

## Entry points (triggers)

| # | Trigger | Where | Keyword |
|---|---------|-------|---------|
| T1 | Comment keyword on post/reel | All teaser & launch posts | `FÊTE` (also accept `FETE`, `fête`, `🎄`) |
| T2 | Story reply / story keyword | Countdown & reveal stories | `FÊTE` |
| T3 | DM keyword | Bio CTA, highlights | `FÊTE`, `LISTE`, `ENTREPRISE`, `NOUVEL AN` |
| T4 | Click-to-Instagram-Direct ads | See `ads-structure.md` C3 | Ad's pre-filled questions |
| T5 | Ice breakers (first-open menu) | Any new conversation | 4 buttons, below |
| T6 | Default reply (any other message) | Fallback | Menu + human handoff |

**Ice breakers (T5), max 4:**
1. 🎁 Rejoindre la Liste Privée
2. 🏢 Organiser la fête de mon entreprise
3. 🥂 Réserver le Nouvel An
4. 📍 Infos & réservation

**Public comment auto-reply (T1)** (rotate 3 variants so it doesn't look botted):
- « Envoyé en DM ✨ Regarde tes messages ! »
- « C'est dans ta boîte 🎁 »
- « Check tes DM, on t'a gardé une place 🔥 »

---

## Flow A — Liste Privée (B2C), triggered by T1/T2/T3 `FÊTE`/`LISTE`, T5 button 1

```
A1  Bonsoir {first_name} ✨
    Bienvenue chez GRADI Festif Expérience 🌙
    Dîner, musique, danse : le nouveau supper club de Genève.
    Eat late, stay later.

    On ouvre le jeudi 5 novembre. Les membres de la Liste Privée ont :
    🥂 un cocktail de bienvenue offert
    🗓️ un accès prioritaire aux réservations dès mardi 3 nov. à 18h
    🎟️ une chance d'être invité·e à la Preview Night (mardi 3 nov.)

    Tu veux en faire partie ?
    [ Oui, je m'inscris ✦ ]   [ C'est quoi GRADI ? ]

A1b (C'est quoi GRADI ?) → « On dîne tard, on reste plus tard encore. Une table, puis la
    musique, puis la piste. » + reveal reel link → back to [ Oui, je m'inscris ]

A2  Condition: follows @[HANDLE]?
    NO  → « Dernière étape : abonne-toi à @[HANDLE] pour débloquer ton
           invitation 🔓 puis appuie sur le bouton 👇 »
           [ C'est fait ✅ ] → re-check (max 2 loops, then continue anyway)
    YES → A3

A3  Parfait. À quel numéro WhatsApp on t'envoie ton invitation ?
    (On l'utilise uniquement pour GRADI, promis.)
    → Collect phone (validate +41 / +33 / 07x format)  → tag: lead_b2c
    [ Je préfère l'email ] → collect email

A4  Tu viendrais plutôt…
    [ En couple 💫 ] [ Entre amis 🎉 ] [ En famille 🎄 ] [ Pour le boulot 🏢 ]
    → set custom field party_type  (« Pour le boulot » → jump to Flow B)

A5  C'est noté {first_name} ✅ Tu es sur la Liste Privée (n° {list_number}).
    On t'envoie ton lien de réservation prioritaire sur WhatsApp
    mardi 3 novembre à 18h, avant tout le monde.

    Un bonus : partage notre dernier post en story et identifie @[HANDLE].
    On tire au sort 10 duos pour la Preview Night de mardi 🎟️
    (tirage lundi 2 nov. à 20h)

    [ Voir le menu des fêtes ]  → landing.html?utm_source=ig_dm&utm_campaign=liste
```
Tags: `lead_b2c`, `follower_verified`, `party_type:*`. Send to Google Sheet / CRM via ManyChat → Zapier.

---

## Flow B — Fêtes d'Entreprise (B2B), triggered by `ENTREPRISE`, T5 button 2, A4 "Pour le boulot"

```
B1  Organiser la fête de fin d'année, c'est souvent un casse-tête.
    On s'occupe de tout : menu, ambiance, animation, facture entreprise.

    Je t'envoie notre Kit Fêtes d'Entreprise 2026 (menus, prix,
    capacités, dates encore libres) ? Et si tu veux goûter avant de
    réserver, on t'invite à notre Soirée Découverte Entreprises
    le mercredi 11 novembre.
    [ Oui, envoie le kit 📄 ]

B2  Pour quelle entreprise ?          → field company
B3  Combien de personnes environ ?
    [ 10-20 ] [ 20-50 ] [ 50-100 ] [ 100+ ]   → field group_size
B4  Quelle période ?
    [ Novembre ] [ 1-10 déc ] [ 11-20 déc ] [ Pas encore fixé ]
B5  Ton email pro pour recevoir le kit ?  → field email  → tag lead_b2b
B6  C'est envoyé 📩 Valbon, notre responsable événements, te rappelle sous
    24h pour bloquer une date (les vendredis partent en premier).
    [ Me rappeler maintenant 📞 ] → notify team (live chat + WhatsApp alert)
```
Automation: email with PDF sent instantly, Slack/WhatsApp alert to Valbon with all fields, and
a 24h follow-up task. If group_size ≥ 50 → **priority, call within 2h**.

---

## Flow C — Nouvel An, triggered by `NOUVEL AN`, T5 button 3, NYE ads

```
C1  Le 31 décembre chez GRADI : le dîner, minuit, puis la piste jusqu'au
    bout de la nuit 🎆  Places limitées à [CAPACITÉ].
    [ Voir les formules ]  [ Me prévenir de la pré-vente ]
C2  (pré-vente) → collect phone → tag nye_interest
    « Tu seras prévenu·e 1h avant tout le monde. Early-bird : -20% pendant 48h. »
```

---

## Flow D — Infos & réservation (T5 button 4, default reply T6)

```
D1  📍 [ADRESSE] · 🕖 [HORAIRES]
    [ Réserver une table ] → booking link with UTM
    [ Voir le menu ]  [ Parler à quelqu'un 👋 ]
```
"Parler à quelqu'un" → pause automation 24h for this contact + notify the live chat inbox.
**Rule: a human replies in < 15 min, 10:00–23:00.**

---

## Human welcome DM to new followers (manual, ≤ 30/day, vary wording)

> Hello {prénom} 👋 Merci pour le follow ! On ouvre GRADI ce jeudi 5 novembre à Genève.
> Si tu veux être sur la Liste Privée (cocktail offert + accès prioritaire), réponds juste
> « FÊTE » ici 🎁

Their reply triggers Flow A automatically. Priority order: local profiles, people who also
liked or commented, creators, company profiles.

---

## Follow-up sequence (inside Instagram's 24h window, then WhatsApp)

| When | Channel | Message |
|------|---------|---------|
| +2h if flow not finished | IG DM | « Ton invitation t'attend encore ✨ [Terminer] » (once only) |
| +23h if no booking & no phone | IG DM | Last message in the window: menu teaser + [Rejoindre la liste] |
| Mon 2 Nov 19:00 | WhatsApp (opt-in) | « Demain 18h, les réservations s'ouvrent pour la Liste Privée uniquement. Mets une alarme ⏰ » |
| Tue 3 Nov 18:00 | WhatsApp | Priority booking link (24h, before public) |
| Wed 4 Nov 12:00 if not booked | WhatsApp | « Ouverture demain. Il reste quelques tables pour le week-end. » |
| Fri 6 Nov if not booked | WhatsApp | « Il reste 6 tables ce samedi… » |
| 16 Nov | WhatsApp | NYE pre-sale (to tag nye_interest first, then everyone) |

Instagram rule: outside the 24h window, a business account can only send messages with an
approved tag (e.g. `HUMAN_AGENT` for manual replies within 7 days). **Never use tags for promos.**
That's why we move people to WhatsApp/email with explicit opt-in as fast as possible.

## QA before go-live
- [ ] Each keyword tested from a personal account (incl. accents/emoji variants)
- [ ] Follow-check works for followers and non-followers
- [ ] Phone validation accepts +41, +33, 07x
- [ ] Zapier → Google Sheet row created with all fields + source tag
- [ ] B2B alert reaches Valbon within 1 min
- [ ] Opt-in wording present before WhatsApp collection
