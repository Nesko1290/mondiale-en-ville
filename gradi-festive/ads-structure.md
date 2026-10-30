# GRADI FESTIVE EXPERIENCE — Ads Structure

Reference budget: **CHF 8,000 for 2 Nov → 31 Dec** (~CHF 135/day on average). It scales
linearly: keep the percentages, change the totals. All customer-facing copy in French.

## Account setup (before spending a franc)
- Meta Pixel + **Conversions API** on `landing.html` and the booking tool
- Events: `Lead` (form/DM lead), `Contact` (WhatsApp click), `Schedule` (table booked),
  `Purchase` (NYE ticket / corporate deposit, with value in CHF)
- Custom audiences created on day 1 so they fill up: IG engagers 30/60d, video viewers 50%/95%,
  landing visitors, DM contacts (ManyChat → Meta audience sync), lead list upload (weekly)
- Age **18+** on every ad set (alcohol on screen). Geo: Geneva canton + 15 km (includes Nyon,
  Annemasse, Ferney, Saint-Julien). Exclude "employees/staff" custom list.
- Naming: `GRADI_{Phase}_{Objective}_{Audience}_{Creative}_{Date}`

---

## Campaign map (Meta)

| # | Campaign | Objective | Dates | Budget | % |
|---|----------|-----------|-------|--------|---|
| **C1** | Teaser / Awareness | Engagement → Video views (ThruPlay) | 2–15 Nov | CHF 900 | 11% |
| **C2** | Liste Privée (B2C leads) | Leads, Instant Form (higher-intent version) | 9–26 Nov | CHF 1,800 | 22% |
| **C3** | Click-to-DM | Engagement → Messaging (Instagram Direct) | 9 Nov–20 Dec | CHF 1,200 | 15% |
| **C4** | Fêtes d'Entreprise (B2B) | Leads (Instant Form + landing) | 2 Nov–10 Dec | CHF 1,200 | 15% |
| **C5** | Opening & December bookings | Sales/Leads → conversion `Schedule` | 25 Nov–24 Dec | CHF 1,700 | 21% |
| **C6** | Nouvel An | Sales → `Purchase` | 1–30 Dec | CHF 800 | 10% |
| **C7** | Always-on retargeting | Sales → `Schedule` | 16 Nov–31 Dec | CHF 400 | 5% |

Plus **Google Search CHF 600** and **LinkedIn CHF 500** (below). Total ≈ CHF 9,100 with
optional channels, or CHF 8,000 if LinkedIn is replaced by more Meta B2B.

### C1 — Teaser / Awareness (build the warm pool cheaply)
- **Ad set 1:** Broad Geneva 18-45, Advantage+ placements (Reels + Stories priority)
- **Ad set 2:** Interests: restaurants, cocktails, nightlife, fine dining, Christmas markets,
  rooftop bars Geneva
- Creatives: 3 vertical reels, 6-12 s
  - *R1 Mystery:* dark room, a match strikes, candles light up one by one → « Quelque chose s'allume à Genève. 27.11 »
  - *R2 Chef:* hands, fire, plating in slow motion → « Le menu des fêtes que Genève attendait. »
  - *R3 Build:* time-lapse of the decor → « 28 jours. Une adresse. Vos fêtes. »
- KPI: CPM < CHF 8, ThruPlay < CHF 0.04, profile visits. **No booking expected.** C1 exists
  to feed C2/C3/C7.

### C2 — Liste Privée (B2C leads)
- **Ad set 1 (warm):** C1 video viewers 50% + IG engagers 30d → highest volume, lowest CPL
- **Ad set 2 (cold broad):** Geneva 22-45, Advantage+ audience
- **Ad set 3 (lookalike):** 1-3% LAL from the lead list (switch on when list > 300)
- Instant Form "higher intent": first name, phone, email, *« Avec qui viendrez-vous ? »*,
  WhatsApp opt-in checkbox. Thank-you screen → `landing.html` / Instagram profile
- Creatives:
  - *Static:* « Liste Privée · Cocktail offert · Accès prioritaire » on a warm festive table shot
  - *Reel UGC-style:* creator: « J'ai pu visiter le nouveau resto des fêtes à Genève… »
  - *Counter:* « 843 Genevois sont déjà sur la liste. » (update weekly, real numbers only)
- KPI: CPL < CHF 2.50. Kill an ad above CHF 4 after CHF 40 spend.

### C3 — Click-to-Instagram-Direct (feeds the DM machine)
- Destination: Instagram Direct, with ManyChat **ad-trigger** (see `dm-automation.md`, T4)
- Pre-filled questions (= buttons in the ad's chat): « 🎁 Je veux l'invitation », « 🏢 Fête d'entreprise », « 🥂 Nouvel An »
- Ad sets: warm (engagers + viewers), cold broad Geneva
- Why: DM leads convert 2-3× better than forms because we can talk to them
- KPI: cost per conversation started < CHF 1.50, flow completion > 55%

### C4 — Fêtes d'Entreprise (B2B, highest value)
- **Ad set 1:** Job titles/interests: HR, office manager, executive assistant, event planning,
  team building; Geneva + 15 km, 25-60
- **Ad set 2:** Employers in Geneva business sectors (banking, trading, watchmaking, NGOs/UN),
  via interests and behaviours where available
- Offer: *Kit Fêtes d'Entreprise 2026* (PDF) + « Les vendredis de décembre partent en premier »
- Form: company, group size, preferred dates, pro email, phone → alert to Valbon < 1 min
- Creatives: group table of 30 guests laughing; carousel « Menu · Ambiance · Facture entreprise · Zéro stress »
- KPI: CPL < CHF 25, lead → quote call 90%, quote → booking 30%

### C5 — Opening & December bookings
- **Ad set 1:** All leads + DM contacts (custom audience) → « Vos réservations prioritaires sont ouvertes »
- **Ad set 2:** Warm pool (viewers, engagers, landing visitors) excluding bookers
- **Ad set 3:** Advantage+ broad with real Preview Night content (after J-2)
- Creatives switch to **real footage from Preview Night and opening**: guests, creators, the
  show moment. Scarcity copy: « Plus que 6 tables ce samedi »
- KPI: cost per booking < CHF 12 (avg table CHF 180+)

### C6 — Nouvel An
- Wave 1 (1–3 Dec): leads tagged `nye_interest` + all leads → early-bird -20%, 48h
- Wave 2 (4–20 Dec): warm pool + LAL of bookers
- Wave 3 (21–30 Dec): « Dernières places », only if seats remain
- KPI: ROAS ≥ 10×

### C7 — Always-on retargeting (exclude bookers last 30d)
- Landing visitors 14d, DM started but not finished, IG engagers 14d
- Rotating ads: reviews/UGC, menu close-ups, « On vous garde une table ? »
- Frequency cap ~3/week

---

## Google Search (CHF 600, 2 Nov–24 Dec)
| Ad group | Keywords (phrase/exact) |
|----------|-------------------------|
| Fête entreprise | "repas de fin d'année entreprise genève", "soirée de noël entreprise genève", "restaurant groupe genève" |
| Restaurant fêtes | "restaurant noël genève", "dîner de fêtes genève", "nouveau restaurant genève" |
| Nouvel An | "réveillon genève", "nouvel an restaurant genève", "soirée 31 décembre genève" |
Headlines: « Fête d'Entreprise Clé en Main », « Menus de Groupe dès CHF [X] », « Réveillon 2026 à Genève ».
Sitelinks: Kit Entreprise, Menu des Fêtes, Nouvel An, Réserver. Bid: Max conversions after 15 conversions.

## LinkedIn (optional, CHF 500, 2–25 Nov)
- Lead Gen Form, Kit Fêtes d'Entreprise
- Targeting: Geneva area, job functions HR / Administrative, seniority Manager+, company size 50+
- Plus: personal posts from the founders (free, and often better than the ads)

---

## Optimisation rules (every morning)
1. Ad above 2× target CPL after spend = 2× target CPL → pause
2. Ad set below target CPL for 3 days → +20% budget (never more than +20% per day)
3. Creative frequency > 3.5 on warm → new creative
4. Every Monday: re-sync lead list to Meta, refresh lookalikes, re-balance budget across C2/C3/C4
   toward the lowest **cost per booking**, not cost per lead
5. Real content beats produced content after J-2: switch C5/C7 to UGC within 24h of Preview Night

## Creative production list (minimum)
| ID | Format | Campaign | Due |
|----|--------|----------|-----|
| R1-R3 | Reels 9:16, 6-12 s | C1 | 1 Nov |
| S1-S3 | Statics 4:5 + 9:16 | C2, C3 | 6 Nov |
| UGC1-3 | Creator reels | C2, C5 | 10 Nov |
| B1-B2 | Carousel + static B2B | C4 | 1 Nov |
| PN1-5 | Preview Night recap reels | C5, C7 | 26 Nov |
| NYE1-3 | Reels + statics | C6 | 30 Nov |
