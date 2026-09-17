-- Steadfast — initial schema
-- Run this in your Supabase project's SQL Editor once. Safe to run only once per project.

-- ---------------------------------------------------------------------------
-- Profiles: one private row per account, holds the streak state
-- ---------------------------------------------------------------------------

create table if not exists profiles (
  id uuid primary key references auth.users (id) on delete cascade,
  name text not null,
  last_relapse_at timestamptz,
  longest_streak_days int not null default 0,
  created_at timestamptz not null default now()
);

-- Auto-create a profile row whenever someone signs up.
create or replace function public.handle_new_auth_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  insert into profiles (id, name)
  values (new.id, coalesce(new.raw_user_meta_data ->> 'full_name', split_part(new.email, '@', 1)))
  on conflict (id) do nothing;
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_auth_user();

-- ---------------------------------------------------------------------------
-- Daily check-ins (doubles as the journal)
-- ---------------------------------------------------------------------------

create table if not exists checkins (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  day date not null,
  status text not null check (status in ('clean', 'relapse')),
  mood smallint check (mood between 1 and 5),
  note text,
  created_at timestamptz not null default now(),
  unique (user_id, day)
);

-- ---------------------------------------------------------------------------
-- Urge tool usage log
-- ---------------------------------------------------------------------------

create table if not exists urge_logs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  outcome text not null check (outcome in ('resisted', 'relapsed')),
  note text,
  created_at timestamptz not null default now()
);

-- ---------------------------------------------------------------------------
-- Row Level Security — every row is private to the account that owns it
-- ---------------------------------------------------------------------------

alter table profiles enable row level security;
alter table checkins enable row level security;
alter table urge_logs enable row level security;

create policy "profiles: read own" on profiles for select to authenticated using (auth.uid() = id);
create policy "profiles: update own" on profiles for update to authenticated using (auth.uid() = id) with check (auth.uid() = id);

create policy "checkins: read own" on checkins for select to authenticated using (auth.uid() = user_id);
create policy "checkins: insert own" on checkins for insert to authenticated with check (auth.uid() = user_id);
create policy "checkins: update own" on checkins for update to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "checkins: delete own" on checkins for delete to authenticated using (auth.uid() = user_id);

create policy "urge_logs: read own" on urge_logs for select to authenticated using (auth.uid() = user_id);
create policy "urge_logs: insert own" on urge_logs for insert to authenticated with check (auth.uid() = user_id);
