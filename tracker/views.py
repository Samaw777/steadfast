from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render
from django.templatetags.static import static
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from . import studies, verses
from .forms import CheckinForm, SignUpForm, StudyEntryForm
from .models import Checkin, StudyEntry

def _icon(path, size, purpose="any"):
    return {"src": static(path), "sizes": f"{size}x{size}", "type": "image/png", "purpose": purpose}


def manifest(request):
    """Makes the site installable as a home-screen app that opens on the home page."""
    data = {
        "name": "Steadfast",
        "short_name": "Steadfast",
        "description": "Track your streak, check in daily, and grow in the Word.",
        "id": "/",
        "start_url": "/",
        "scope": "/",
        "display": "standalone",
        "background_color": "#0a1214",
        "theme_color": "#0a1214",
        "icons": [
            _icon("icons/icon-192.png", 192),
            _icon("icons/icon-512.png", 512),
            _icon("icons/icon-maskable-512.png", 512, "maskable"),
        ],
    }
    return JsonResponse(data, content_type="application/manifest+json")


def greeting():
    hour = timezone.localtime().hour
    if hour < 12:
        return "Good morning"
    if hour < 18:
        return "Good afternoon"
    return "Good evening"


@require_http_methods(["GET", "POST"])
def signup(request):
    if request.user.is_authenticated:
        return redirect("home")
    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("home")
    return render(request, "registration/signup.html", {"form": form})


MILESTONES = [1, 3, 7, 14, 30, 60, 90, 180, 365]


def milestone_progress(streak):
    """Where the streak sits between the last milestone reached and the next one."""
    previous = max([m for m in MILESTONES if m <= streak], default=0)
    upcoming = next((m for m in MILESTONES if m > streak), None)
    if upcoming is None:  # past a year: aim for the next full year
        previous = streak // 365 * 365
        upcoming = previous + 365
    percent = round((streak - previous) / (upcoming - previous) * 100)
    return {
        "next": upcoming,
        "days_left": upcoming - streak,
        "percent": percent,
        # The hero's sun climbs from just behind the ridge (y=125) toward the top of the sky (y=40).
        "sun_y": round(125 - percent * 0.85),
    }


def week_strip(user, today):
    """The last 7 days, oldest first, each with that day's check-in status (or None)."""
    days = [today - timedelta(days=offset) for offset in range(6, -1, -1)]
    statuses = dict(user.checkins.filter(day__gte=days[0]).values_list("day", "status"))
    return [{"day": day, "status": statuses.get(day), "is_today": day == today} for day in days]


@login_required
def home(request):
    user = request.user
    today = timezone.localdate()
    streak = user.current_streak_days()
    week = week_strip(user, today)
    best = max(streak, user.longest_streak_days)
    return render(
        request,
        "tracker/home.html",
        {
            "greeting": greeting(),
            "today": today,
            "streak": streak,
            "best": best,
            "progress": milestone_progress(streak),
            "week": week,
            "week_checkins": sum(1 for d in week if d["status"]),
            "checked_in_today": week[-1]["status"] is not None,
            "milestones": [{"days": m, "earned": best >= m} for m in MILESTONES],
            "studies_done": user.study_entries.count(),
            "verse": verses.verse_of_the_day(today),
        },
    )


@login_required
@require_http_methods(["GET", "POST"])
def checkin(request):
    today = timezone.localdate()
    existing = Checkin.objects.filter(user=request.user, day=today).first()
    already_slipped = existing is not None and existing.status == Checkin.Status.RELAPSE
    initial = {"status": Checkin.Status.CLEAN}
    form = CheckinForm(request.POST or None, instance=existing, initial=initial)
    confirming_relapse = False

    if request.method == "POST" and form.is_valid():
        is_new_relapse = form.cleaned_data["status"] == Checkin.Status.RELAPSE and not already_slipped
        if is_new_relapse and "confirm" not in request.POST:
            confirming_relapse = True
        else:
            with transaction.atomic():
                entry = form.save(commit=False)
                entry.user = request.user
                entry.day = today
                entry.save()
                if is_new_relapse:
                    request.user.log_relapse()
            messages.success(request, "Check-in saved.")
            return redirect("home")

    return render(
        request,
        "tracker/checkin.html",
        {"form": form, "today": today, "confirming_relapse": confirming_relapse},
    )


@login_required
def journal(request):
    return render(
        request,
        "tracker/journal.html",
        {"entries": request.user.checkins.all(), "today": timezone.localdate()},
    )


def study_progress(user):
    """Which plan days this person has finished, and the next one to do."""
    done = set(user.study_entries.values_list("slug", flat=True))
    upcoming = next((study for study in studies.STUDIES if study.slug not in done), None)
    progress = {
        "done": done,
        "count": len(done & studies.BY_SLUG.keys()),
        "total": len(studies.STUDIES),
        "next": upcoming,
        "percent": round(len(done & studies.BY_SLUG.keys()) / len(studies.STUDIES) * 100),
    }
    progress["sun_y"] = round(125 - progress["percent"] * 0.85)
    return progress


@login_required
def study_index(request):
    plan = study_progress(request.user)
    days = [{"study": study, "done": study.slug in plan["done"]} for study in studies.STUDIES]
    return render(
        request,
        "tracker/study_index.html",
        {"plan": plan, "days": days, "plan_title": studies.PLAN_TITLE, "plan_summary": studies.PLAN_SUMMARY},
    )


@login_required
@require_http_methods(["GET", "POST"])
def study_detail(request, slug):
    study = studies.BY_SLUG.get(slug)
    if study is None:
        raise Http404("No such study.")
    entry = StudyEntry.objects.filter(user=request.user, slug=slug).first()
    form = StudyEntryForm(request.POST or None, instance=entry)

    if request.method == "POST" and form.is_valid():
        saved = form.save(commit=False)
        saved.user = request.user
        saved.slug = slug
        saved.save()
        plan = study_progress(request.user)
        if plan["next"] is None:
            messages.success(request, f"You finished {studies.PLAN_TITLE}. Well done!")
        elif entry is None:
            messages.success(request, f"Day {study.day} complete. See you tomorrow.")
        else:
            messages.success(request, "Reflection saved.")
        return redirect("study")

    position = studies.STUDIES.index(study)
    return render(
        request,
        "tracker/study_detail.html",
        {
            "study": study,
            "form": form,
            "entry": entry,
            "total": len(studies.STUDIES),
            "previous": studies.STUDIES[position - 1] if position > 0 else None,
            "following": studies.STUDIES[position + 1] if position + 1 < len(studies.STUDIES) else None,
        },
    )
