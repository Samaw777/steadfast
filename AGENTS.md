# Working on Steadfast

Django 5.2 app with server-rendered templates; Supabase is used only as the Postgres database
(Django handles accounts). See README.md for the layout.

- Set up: `python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt`
- Run tests: `python manage.py test` (uses SQLite unless `DATABASE_URL` is set)
- Run locally: `DEBUG=1 python manage.py runserver`
- After changing models: `python manage.py makemigrations tracker` and commit the migration.
- Keep every table private: `tracker/apps.py` enables Row Level Security on all Django tables after
  each `migrate`, because Supabase exposes the `public` schema via its REST API.
- Templates live in the project-level `templates/` folder (it must take precedence over
  `django.contrib.admin`'s own `registration/` templates); all styles are in `static/css/app.css`.
