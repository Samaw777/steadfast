# Steadfast

A private, single-user recovery tracker: streak counter, daily check-ins with mood and notes,
a journal of past check-ins, an in-the-moment urge tool, and a rotating scripture verse. Each
account only ever sees its own data.

## Stack

- [Django 5.2](https://www.djangoproject.com/) (LTS) with server-rendered templates — no JavaScript build step
- [Supabase](https://supabase.com) Postgres as the database
- Django's built-in accounts (sign up with email, sign in, password reset)
- [WhiteNoise](https://whitenoise.readthedocs.io/) for static files, [Gunicorn](https://gunicorn.org/) in production
- Deploys free on [Render](https://render.com) — see [DEPLOY.md](DEPLOY.md)

## Project layout

```
config/            Django project: settings, root URLs, WSGI
tracker/           The app: models, views, forms, tests
  models.py        User (email login + streak state), Checkin, UrgeLog
  views.py         Home, check-in, journal, urge tool, sign-up
  verses.py        Scripture lists and verse-of-the-day
  apps.py          Turns on Row Level Security for every table after `migrate` (see below)
  middleware.py    Uses the browser's timezone so "today" matches your clock
templates/         All HTML templates
static/css/app.css The whole stylesheet
```

## Local development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env        # then fill in SECRET_KEY and DATABASE_URL
python manage.py migrate    # creates the tables in your Supabase database
python manage.py runserver
```

Open <http://localhost:8000>, create an account, and it's ready to use.

- Leave `DATABASE_URL` empty to use a local SQLite file instead of Supabase.
- `python manage.py createsuperuser` gives you the Django admin at `/admin/`.
- Without SMTP settings, password reset emails are printed in the `runserver` output.

Run the tests with:

```bash
python manage.py test
```

## How the streak works

Each account has a `last_relapse_at` timestamp (empty until the first slip). The current streak is
the number of full days since that timestamp, or since sign-up if there hasn't been a slip yet.
Logging a slip — from the daily check-in or the urge tool — banks the streak that just ended into
`longest_streak_days` if it's a new record, then resets the clock. Editing a check-in that was
already marked as a slip doesn't reset the clock a second time.

## Supabase and data privacy

Django talks to Supabase as a plain Postgres database and handles accounts itself, so the
Supabase "Authentication" section isn't used.

Supabase also exposes the `public` schema through its auto-generated REST API, reachable with the
project's public anon key. To keep that from leaking anything, every `migrate` turns on Row Level
Security for all Django tables with no policies attached: the REST API sees nothing, while Django
(connecting as the table owner) works normally.
