# Steadfast

A private, single-user recovery tracker: streak counter, daily check-ins with mood and notes,
an in-the-moment urge tool, and a rotating scripture verse. Each account only ever sees its own
data.

## Stack

- [Next.js](https://nextjs.org) (App Router) + TypeScript
- [Tailwind CSS](https://tailwindcss.com)
- [Supabase](https://supabase.com) — auth + Postgres database
- Deploys free on [Vercel](https://vercel.com)

## Local development

1. Copy `.env.example` to `.env.local` and fill in your Supabase project URL and anon key (see
   [DEPLOY.md](DEPLOY.md) for how to get a free Supabase project).
2. Run the SQL in `supabase/migrations/001_init.sql` in your Supabase project's SQL Editor.
3. Install dependencies and start the dev server:

   ```
   npm install
   npm run dev
   ```

4. Open [http://localhost:3000](http://localhost:3000), create an account, and it's ready to use.

## How the streak works

Each account has a `last_relapse_at` timestamp (null until the first slip). The current streak is
just the number of full days since that timestamp, or since the account was created if there
hasn't been a slip yet. Logging a slip — from the daily check-in or the urge tool — banks the
streak that just ended into `longest_streak_days` if it's a new record, then resets the clock.

## Deploying

See [DEPLOY.md](DEPLOY.md) for step-by-step, free-tier deployment instructions.
