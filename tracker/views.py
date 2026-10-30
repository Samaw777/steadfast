import random
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from . import verses
from .forms import CheckinForm, SignUpForm
from .models import Checkin, UrgeLog

DISTRACTIONS = [
    "Step outside for a few minutes, even just to a doorway or balcony.",
    "Call or text someone you trust — you don't have to explain why.",
    "Do 20 push-ups or go for a brisk walk.",
    "Put on music and change the room you're in.",
    "Write down what you're feeling right now, in one sentence.",
    "Splash cold water on your face.",
    "Pick up a book or podcast you've been meaning to get to.",
]


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
            "urges_resisted": user.urge_logs.filter(outcome=UrgeLog.Outcome.RESISTED).count(),
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


@login_required
@require_http_methods(["GET", "POST"])
def urge(request):
    confirming_relapse = False
    outcome = request.POST.get("outcome")

    if request.method == "POST" and outcome == UrgeLog.Outcome.RESISTED:
        UrgeLog.objects.create(user=request.user, outcome=outcome)
        return render(request, "tracker/urge_done.html", {"outcome": outcome})

    if request.method == "POST" and outcome == UrgeLog.Outcome.RELAPSED:
        if "confirm" in request.POST:
            with transaction.atomic():
                UrgeLog.objects.create(user=request.user, outcome=outcome)
                request.user.log_relapse()
            return render(request, "tracker/urge_done.html", {"outcome": outcome})
        confirming_relapse = True

    return render(
        request,
        "tracker/urge.html",
        {
            "verse": verses.random_verse(verses.TEMPTATION),
            "distraction": random.choice(DISTRACTIONS),
            "confirming_relapse": confirming_relapse,
        },
    )
