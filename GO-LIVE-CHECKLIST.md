# MONDIALE EN VILLE — Go-Live Checklist (deadline 2026-05-11)

## 1. Site (already built)
- [ ] Decide final domain (mondialeenville.ch? .com?)
- [ ] Buy domain if not owned
- [ ] Choose host: Hostinger (current Brian default) or Infomaniak (Swiss-hosted, better for .ch domain + local SEO)
- [ ] Deploy `index.html` + `billetterie.html` + assets
- [ ] Configure HTTPS (Let's Encrypt — both hosts auto)
- [ ] Add favicon + OG share image (1200x630)
- [ ] Test on mobile (iOS Safari + Android Chrome)
- [ ] Test on desktop (Chrome, Safari, Firefox)
- [ ] Verify all internal links work (index ↔ billetterie)
- [ ] Verify French copy throughout (no English leaks)
- [ ] Check page speed (target: LCP < 2.5s)

## 2. Ticketing wiring (CRITICAL — biggest risk)
- [ ] Choose backend: **FourVenues** (already referenced in design system) OR Stripe Checkout direct
- [ ] Create venue/event in chosen platform
- [ ] Configure ticket tiers (Standard / VIP / Lounge?)
- [ ] Set pricing in CHF
- [ ] Embed ticket widget in `billetterie.html`
- [ ] Test full purchase flow with real card (€1 test ticket)
- [ ] Confirm payout account is Maikel's
- [ ] Set up confirmation email template (in French)
- [ ] Add ticket sales tracking pixel (Meta + Google)

## 3. Tracking & Analytics
- [ ] Install Google Analytics 4
- [ ] Install Meta Pixel
- [ ] Install TikTok Pixel (if running TikTok ads)
- [ ] Configure conversion events: `ViewContent`, `InitiateCheckout`, `Purchase`
- [ ] Test events with Meta Pixel Helper extension

## 4. Legal / Compliance
- [ ] Add cookie banner (RGPD — required in EU/CH)
- [ ] Add Mentions Légales page (required in France/CH)
- [ ] Add CGV (conditions générales de vente) for ticket sales
- [ ] Add privacy policy

## Owner mapping
| Item                          | Owner   |
|-------------------------------|---------|
| Domain & deployment           | Brian   |
| Ticketing backend wiring      | Brian   |
| Tracking pixels               | Brian   |
| Venue contracts (locked)      | Valbon  |
| Staff confirmed for openings  | Valbon  |
| Cookie banner / legal pages   | Brian (with Valbon's input on company name) |
| Payout account verified       | Maikel  |
