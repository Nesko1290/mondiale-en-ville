# GRADI FESTIVE EXPERIENCE — Ads Structure

Reference budget: **CHF 8,000 for 31 Oct → 31 Dec**. It scales linearly: keep the
percentages, change the totals. All customer-facing copy in French.

**Opening is Thu 5 Nov, so ads go live Sat 31 Oct.** That means ~CHF 300/day for the first 5
days (heavy on purpose) and ~CHF 110/day afterwards. With only 5 days before opening, Meta's
learning phase won't finish, so: **few ad sets, broad audiences, Advantage+ placements, and
no edits during the first 48h except killing clear losers.**

## Account setup (before spending a franc)
- Meta Pixel + **Conversions API** on `landing.html` and the booking tool
- Events: `Lead` (form/DM lead), `Contact` (WhatsApp click), `Schedule` (table booked),
  `Purchase` (NYE ticket / corporate deposit, with value in CHF)
- Custom audiences created on 30 Oct so they fill up: IG engagers 30/60d, video viewers 50%/95%,
  landing visitors, DM contacts (ManyChat → Meta audience sync), lead list upload (weekly)
- Age **18+** on every ad set (alcohol on screen). Geo: Geneva canton + 15 km (includes Nyon,
  Annemasse, Ferney, Saint-Julien). Exclude "employees/staff" custom list.
- Naming: `GRADI_{Phase}_{Objective}_{Audience}_{Creative}_{Date}`

---

## Campaign map (Meta)

| # | Campaign | Objective | Dates | Budget | % |
|---|----------|-----------|-------|--------|---|
| **C1** | Reveal / Awareness | Engagement → Video views (ThruPlay) | 31 Oct–4 Nov | CHF 500 | 6% |
| **C2** | Liste Privée (B2C leads) | Leads, Instant Form (higher-intent version) | 31 Oct–4 Nov | CHF 1,000 | 13% |
| **C3** | Click-to-DM | Engagement → Messaging (Instagram Direct) | 31 Oct–20 Dec | CHF 1,300 | 16% |
| **C4** | Fêtes d'Entreprise (B2B) | Leads (Instant Form + landing) | 31 Oct–10 Dec | CHF 1,400 | 18% |
| **C5** | Opening & bookings | Sales/Leads → conversion `Schedule` | 3 Nov–24 Dec | CHF 2,000 | 25% |
| **C6** | Nouvel An | Sales → `Purchase` | 16 Nov–30 Dec | CHF 1,000 | 13% |
| **C7** | Always-on retargeting | Sales → `Schedule` | 4 Nov–31 Dec | CHF 800 | 10% |

**Pre-opening split (31 Oct–4 Nov, ~CHF 1,500):** C2 45% · C1 20% · C3 20% · C4 15%.

Plus **Google Search CHF 600** and **LinkedIn CHF 500** (below). Total ≈ CHF 9,100 with
optional channels, or CHF 8,000 if LinkedIn is replaced by more Meta B2B.

### C1 — Reveal / Awareness (build the warm pool fast, 31 Oct–4 Nov only)
- **One ad set:** Broad Geneva 18-45, Advantage+ placements (Reels + Stories priority)
- Creatives: 3 vertical reels, 6-12 s, all from the 31 Oct shoot
  - *R1 Reveal:* dark room, a match strikes, candles light up one by one → « Gradi s'allume. Jeudi 5 novembre. »
  - *R2 Chef:* hands, fire, plating in slow motion → « Le menu des fêtes que Genève attendait. »
  - *R3 Countdown:* fast cuts of decor, team, cocktails → « Dans 5 jours. Une adresse. Vos fêtes. »
- KPI: CPM < CHF 8, ThruPlay < CHF 0.04, profile visits. **No booking expected.** C1 exists
  to feed C2/C3/C7. Stop it on 4 Nov and move the budget to C5.

### C2 — Liste Privée (B2C leads)
- **Ad set 1 (warm):** C1 video viewers 50% + IG/FB engagers + team's existing followers
- **Ad set 2 (cold broad):** Geneva 22-45, Advantage+ audience
- (No lookalike: the list won't be big enough before opening. Use it later in C5/C6.)
- Offer deadline is real: **priority booking opens Tue 3 Nov 18:00**, so the ad says so.
- Instant Form "higher intent": first name, phone, email, *« Avec qui viendrez-vous ? »*,
  WhatsApp opt-in checkbox. Thank-you screen → `landing.html` / Instagram profile
- Creatives:
  - *Static:* « Liste Privée · Cocktail offert · Accès prioritaire » on a warm festive table shot
  - *Reel UGC-style:* creator: « J'ai pu visiter le nouveau resto des fêtes à Genève… »
  - *Counter:* « 843 Genevois sont déjà sur la liste. » (update weekly, real numbers only)
- KPI: CPL < CHF 2.50. Kill an ad above CHF 4 after CHF 40 spend.
- After 4 Nov: stop C2 and move leftovers into C3 (DM) and C5 (bookings).

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
- Offer: *Kit Fêtes d'Entreprise 2026* (PDF) + « Venez goûter avant de réserver » (invitation to
  the Soirée Découverte Entreprises, Wed 11 Nov) + « Les vendredis de décembre partent en premier »
- Form: company, group size, preferred dates, pro email, phone → alert to Valbon < 1 min
- Creatives: group table of 30 guests laughing; carousel « Menu · Ambiance · Facture entreprise · Zéro stress »
- KPI: CPL < CHF 25, lead → quote call 90%, quote → booking 30%

### C5 — Opening & bookings (Nov + Dec)
- **Ad set 1:** All leads + DM contacts (custom audience) → « Vos réservations prioritaires sont ouvertes »
- **Ad set 2:** Warm pool (viewers, engagers, landing visitors) excluding bookers
- **Ad set 3:** Advantage+ broad with real Preview Night content (after J-2)
- 3–4 Nov: « Ouverture jeudi 5 novembre. Réservez votre table. »
- From 4 Nov: creatives switch to **real footage from Preview Night (Tue 3 Nov) and opening**:
  guests, creators, the show moment. Scarcity copy: « Plus que 6 tables ce samedi »
- KPI: cost per booking < CHF 12 (avg table CHF 180+)

### C6 — Nouvel An
- Wave 1 (16–17 Nov): leads tagged `nye_interest` + all leads → early-bird -20%, 48h
- Wave 2 (18 Nov–20 Dec): warm pool + LAL of bookers and guests
- Wave 3 (21–30 Dec): « Dernières places », only if seats remain
- KPI: ROAS ≥ 10×

### C7 — Always-on retargeting (exclude bookers last 30d)
- Landing visitors 14d, DM started but not finished, IG engagers 14d
- Rotating ads: reviews/UGC, menu close-ups, « On vous garde une table ? »
- Frequency cap ~3/week

---

## Google Search (CHF 600, 1 Nov–24 Dec)
| Ad group | Keywords (phrase/exact) |
|----------|-------------------------|
| Fête entreprise | "repas de fin d'année entreprise genève", "soirée de noël entreprise genève", "restaurant groupe genève" |
| Restaurant fêtes | "restaurant noël genève", "dîner de fêtes genève", "nouveau restaurant genève" |
| Nouvel An | "réveillon genève", "nouvel an restaurant genève", "soirée 31 décembre genève" |
Headlines: « Fête d'Entreprise Clé en Main », « Menus de Groupe dès CHF [X] », « Réveillon 2026 à Genève ».
Sitelinks: Kit Entreprise, Menu des Fêtes, Nouvel An, Réserver. Bid: Max conversions after 15 conversions.

## LinkedIn (optional, CHF 500, 2–20 Nov)
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
5. Real content beats produced content: switch C5/C7 to Preview Night footage by Wed 4 Nov 12:00

## Creative production list (minimum)
| ID | Format | Campaign | Due |
|----|--------|----------|-----|
| R1-R3 | Reels 9:16, 6-12 s | C1 | Sat 31 Oct 16:00 (shoot that morning) |
| S1-S3 | Statics 4:5 + 9:16 | C2, C3 | Sat 31 Oct 16:00 |
| B1-B2 | Carousel + static B2B | C4 | Sat 31 Oct 16:00 |
| UGC1-3 | Creator reels | C5, C7 | Wed 4 Nov (from Preview Night) |
| PN1-5 | Preview Night recap reels | C5, C7 | Wed 4 Nov 12:00 |
| NYE1-3 | Reels + statics | C6 | 14 Nov |
