# Deploying Steadfast

Two free accounts get this live: **Supabase** (database + auth) and **Vercel** (hosting).
You'll also need a **GitHub** account to hold the code.

## 1. Create the Supabase project

1. Go to [supabase.com](https://supabase.com) and sign up / log in.
2. Click **New Project**. Pick a name and a database password (save it somewhere), choose a
   region, and create it — takes about 2 minutes to provision.
3. Once it's ready, open the **SQL Editor** (left sidebar), paste in the entire contents of
   `supabase/migrations/001_init.sql` from this project, and click **Run**. This creates the
   `profiles`, `checkins`, and `urge_logs` tables, the sign-up trigger, and locks every row to
   its own account with Row Level Security.
4. Optional: **Authentication → Providers → Email**, turn off **Confirm email** so you can sign
   in immediately after creating an account instead of waiting on a confirmation email.
5. Go to **Settings → API**. Copy the **Project URL** and the **anon public** key — you'll need
   both in step 3 below.

## 2. Push the code to GitHub

1. Create a new (empty) repository on [github.com](https://github.com/new) — don't initialize it
   with a README.
2. From this project's folder:
   ```
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git push -u origin main
   ```

## 3. Deploy on Vercel

1. Go to [vercel.com](https://vercel.com) and sign up / log in with your GitHub account.
2. Click **Add New → Project**, then select the repo you just pushed.
3. Before deploying, expand **Environment Variables** and add:
   - `NEXT_PUBLIC_SUPABASE_URL` — the Project URL from step 1.5
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY` — the anon key from step 1.5
4. Click **Deploy**. After a minute or two you'll get a live URL like `steadfast.vercel.app`.

## After launch

- **Custom domain**: Vercel → your project → Settings → Domains.
- **Updating the app**: push new commits to `main` on GitHub; Vercel redeploys automatically.
- **Everything is free at this scale**: Supabase's free tier and Vercel's hobby tier both cover a
  single-user app like this comfortably.
