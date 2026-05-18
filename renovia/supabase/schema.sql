-- Renovia — schéma de base
-- À appliquer dans Supabase Studio (SQL editor) ou via `supabase db push`.
-- Idempotent : peut être rejoué sans casser un schéma existant.

-- ---------- Extensions ----------
create extension if not exists "pgcrypto";

-- ---------- profiles ----------
create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  full_name text,
  avatar_url text,
  created_at timestamptz not null default now()
);

alter table public.profiles enable row level security;

drop policy if exists "profiles read own" on public.profiles;
create policy "profiles read own" on public.profiles
  for select using (auth.uid() = id);

drop policy if exists "profiles update own" on public.profiles;
create policy "profiles update own" on public.profiles
  for update using (auth.uid() = id);

-- Trigger : créer automatiquement un profil quand un user s'inscrit
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  insert into public.profiles (id, full_name, avatar_url)
  values (
    new.id,
    coalesce(new.raw_user_meta_data->>'full_name', new.raw_user_meta_data->>'name'),
    new.raw_user_meta_data->>'avatar_url'
  )
  on conflict (id) do nothing;
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();

-- ---------- artisans ----------
create table if not exists public.artisans (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  city text,
  about text,
  rating numeric(2,1) not null default 0,
  reviews_count int not null default 0,
  verified boolean not null default false,
  avatar_url text,
  portfolio jsonb not null default '[]'::jsonb,
  created_at timestamptz not null default now()
);

alter table public.artisans enable row level security;

drop policy if exists "artisans read all" on public.artisans;
create policy "artisans read all" on public.artisans
  for select to authenticated using (true);

-- ---------- projects ----------
create table if not exists public.projects (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  title text,
  type text not null,
  style text,
  rooms int not null default 1,
  surface_m2 numeric(6,2),
  photo_path text,
  rendered_path text,
  status text not null default 'brouillon',
  estimate jsonb,
  analysis jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists projects_user_id_idx on public.projects(user_id);
create index if not exists projects_status_idx on public.projects(status);

alter table public.projects enable row level security;

drop policy if exists "projects read own" on public.projects;
create policy "projects read own" on public.projects
  for select using (auth.uid() = user_id);

drop policy if exists "projects insert own" on public.projects;
create policy "projects insert own" on public.projects
  for insert with check (auth.uid() = user_id);

drop policy if exists "projects update own" on public.projects;
create policy "projects update own" on public.projects
  for update using (auth.uid() = user_id);

drop policy if exists "projects delete own" on public.projects;
create policy "projects delete own" on public.projects
  for delete using (auth.uid() = user_id);

-- ---------- bookings ----------
create table if not exists public.bookings (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references public.projects(id) on delete cascade,
  artisan_id uuid not null references public.artisans(id),
  user_id uuid not null references auth.users(id) on delete cascade,
  scheduled_at timestamptz not null,
  deposit_paid boolean not null default false,
  deposit_chf numeric(10,2),
  total_chf numeric(10,2),
  status text not null default 'reserve',
  created_at timestamptz not null default now()
);

create index if not exists bookings_user_id_idx on public.bookings(user_id);
create index if not exists bookings_project_id_idx on public.bookings(project_id);

alter table public.bookings enable row level security;

drop policy if exists "bookings read own" on public.bookings;
create policy "bookings read own" on public.bookings
  for select using (auth.uid() = user_id);

drop policy if exists "bookings insert own" on public.bookings;
create policy "bookings insert own" on public.bookings
  for insert with check (auth.uid() = user_id);

drop policy if exists "bookings update own" on public.bookings;
create policy "bookings update own" on public.bookings
  for update using (auth.uid() = user_id);

-- ---------- reviews ----------
create table if not exists public.reviews (
  id uuid primary key default gen_random_uuid(),
  booking_id uuid not null references public.bookings(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  artisan_id uuid not null references public.artisans(id),
  rating int not null check (rating between 1 and 5),
  comment text,
  created_at timestamptz not null default now()
);

alter table public.reviews enable row level security;

drop policy if exists "reviews read all" on public.reviews;
create policy "reviews read all" on public.reviews
  for select to authenticated using (true);

drop policy if exists "reviews insert own" on public.reviews;
create policy "reviews insert own" on public.reviews
  for insert with check (auth.uid() = user_id);

-- ---------- Realtime ----------
alter publication supabase_realtime add table public.bookings;
alter publication supabase_realtime add table public.projects;

-- ---------- Storage bucket ----------
insert into storage.buckets (id, name, public)
values ('project-photos', 'project-photos', false)
on conflict (id) do nothing;

-- Politique : un user peut lire/écrire dans son propre dossier user_id/*
drop policy if exists "project photos read own" on storage.objects;
create policy "project photos read own" on storage.objects
  for select using (
    bucket_id = 'project-photos'
    and auth.uid()::text = (storage.foldername(name))[1]
  );

drop policy if exists "project photos insert own" on storage.objects;
create policy "project photos insert own" on storage.objects
  for insert with check (
    bucket_id = 'project-photos'
    and auth.uid()::text = (storage.foldername(name))[1]
  );

drop policy if exists "project photos delete own" on storage.objects;
create policy "project photos delete own" on storage.objects
  for delete using (
    bucket_id = 'project-photos'
    and auth.uid()::text = (storage.foldername(name))[1]
  );
