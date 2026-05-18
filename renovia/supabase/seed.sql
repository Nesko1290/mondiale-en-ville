-- Renovia — seed des artisans de demo.
-- À appliquer apres schema.sql.

insert into public.artisans (name, city, about, rating, reviews_count, verified)
values
  (
    'Peinture & Fils Sàrl',
    'Genève',
    'Entreprise familiale avec 15 ans d''expérience. Spécialisée dans les travaux de peinture intérieure.',
    4.9,
    126,
    true
  ),
  (
    'Renov''Art SA',
    'Lausanne',
    'Artisans certifiés, finitions haut de gamme, intervention rapide.',
    4.7,
    84,
    true
  ),
  (
    'Atelier Murs Suisse',
    'Neuchâtel',
    'Spécialiste enduits, béton ciré et papiers peints sur mesure.',
    4.8,
    62,
    true
  )
on conflict do nothing;
