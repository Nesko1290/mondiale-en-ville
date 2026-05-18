# Supabase — setup Renovia

## 1. Créer le projet

1. Aller sur https://supabase.com → New project
2. Récupérer `Project URL` et `anon public key` (Settings → API)
3. Les copier dans `renovia/.env` :

```
EXPO_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
EXPO_PUBLIC_SUPABASE_ANON_KEY=eyJ...
```

## 2. Appliquer le schéma

Dans Supabase Studio → SQL editor :

1. Coller `schema.sql` → Run
2. Coller `seed.sql` → Run (artisans de démo)

Le schéma est idempotent — peut être rejoué sans casse.

## 3. Activer Apple Sign In

Studio → Authentication → Providers → Apple :
- Service ID (depuis Apple Developer)
- Team ID
- Key ID + clé privée (.p8)

## 4. Activer Google Sign In

Studio → Authentication → Providers → Google :
- Client ID (Web)
- Client Secret

Côté app, ajouter aussi le client iOS dans `.env` :

```
EXPO_PUBLIC_GOOGLE_IOS_CLIENT_ID=...apps.googleusercontent.com
EXPO_PUBLIC_GOOGLE_WEB_CLIENT_ID=...apps.googleusercontent.com
```

Ajouter `renovia://auth-callback` dans les Redirect URLs autorisées.

## 5. Realtime

Les tables `bookings` et `projects` sont publiées sur le canal `supabase_realtime`
(voir fin de `schema.sql`). L'écran Suivi (`app/tracking.tsx`) s'y abonne pour
réagir aux changements de statut.

## 6. Edge Function "render" (IA)

L'écran `app/render.tsx` invoque la function `render` qui appelle Replicate
(SDXL img2img par défaut) avec un prompt dérivé du style choisi.

```bash
# Configurer les secrets
supabase secrets set REPLICATE_API_TOKEN=r8_xxx
# Optionnel : pinner un autre modele
supabase secrets set REPLICATE_MODEL=stability-ai/sdxl:39ed52f2...

# Deployer
supabase functions deploy render
```

L'authentification utilisateur est requise (JWT Supabase) ; la function rejette
les projets qui n'appartiennent pas au caller. Le rendu est reposé dans le
bucket `project-photos` sous `{user_id}/renders/`.

## 7. Edge Function "create-deposit-intent" (Stripe)

L'écran `app/summary.tsx` invoque `create-deposit-intent` au tap "Payer l'acompte".
La function crée un Customer + EphemeralKey + PaymentIntent Stripe pour le
montant de l'acompte stocké dans la table `bookings`. Le client ouvre ensuite
le PaymentSheet natif Stripe.

```bash
supabase secrets set STRIPE_SECRET_KEY=sk_test_xxx
supabase functions deploy create-deposit-intent
```

Côté app, ajouter dans `.env` :

```
EXPO_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_xxx
```

> En prod, remplacer l'update client `markDepositPaid()` par un webhook
> Stripe (`payment_intent.succeeded`) qui flip `bookings.deposit_paid` et
> `bookings.status` côté serveur.

## 8. Storage

Bucket `project-photos` créé en privé. Les fichiers sont rangés par
`{user_id}/{timestamp}.{ext}`. Lecture via signed URL (1h par défaut).
