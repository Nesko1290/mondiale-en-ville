# Renovia

App mobile de rénovation : prends une photo d'une pièce, choisis un style, vois le rendu IA, reçois une estimation et un artisan vérifié.

## Stack

- **Expo SDK 51** + **expo-router** (typed routes)
- **TypeScript** strict
- **NativeWind v4** (Tailwind RN)
- **Zustand** pour l'état du projet en cours
- **expo-camera** pour la prise de photo

## Démarrer

```bash
cd renovia
npm install
cp .env.example .env       # remplir avec les credentials Supabase
npx expo start
```

Configuration Supabase : voir `supabase/README.md`.

Puis scanner le QR avec Expo Go (iOS / Android) ou lancer un simulateur.

## Structure

```
app/                  expo-router routes
  _layout.tsx         stack racine
  index.tsx           1. Splash
  onboarding.tsx      2. Onboarding
  (tabs)/             3. Accueil + tabs
  capture.tsx         4. Prise de photo
  project-type.tsx    5. Type de projet
  style.tsx           6. Choix du style
  render.tsx          7. Résultat IA
  analysis.tsx        8. Analyse du mur
  estimate.tsx        9. Estimation
  artisans.tsx        10. Proposition Renovia
  artisan/[id].tsx    11. Détail artisan
  booking.tsx         12. Réservation
  summary.tsx         13. Récapitulatif
  tracking.tsx        14. Suivi
  done.tsx            15. Projet terminé
components/           UI partagée (Button, Card, Header, Screen)
lib/                  theme, types, store, mock data, formatters
```

## Routes & flux

`/` → `/onboarding` → `/(tabs)` → `/capture` → `/project-type` → `/style` →
`/render` → `/analysis` → `/estimate` → `/artisans` → `/artisan/[id]` →
`/booking` → `/summary` → `/tracking` → `/done`

## Backend (Supabase)

- Auth Apple + Google (`lib/auth.ts`)
- Tables : `profiles`, `artisans`, `projects`, `bookings`, `reviews` (RLS activée)
- Storage bucket privé `project-photos` (path : `{user_id}/{ts}.{ext}`)
- Realtime sur `bookings` + `projects` pour l'écran Suivi
- Schéma + seed : `supabase/schema.sql`, `supabase/seed.sql`

## TODO branchements

- Endpoint IA (ControlNet inpainting) côté serveur ou Edge Function
- Stripe acompte
- Push notifications (`expo-notifications`)
