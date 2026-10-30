from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Checkin, StudyEntry, User


class StreakTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="a@example.com", password="pw-long-enough-1")

    def test_counts_from_signup_until_first_slip(self):
        self.user.date_joined = timezone.now() - timedelta(days=5, hours=3)
        self.assertEqual(self.user.current_streak_days(), 5)

    def test_slip_today_means_zero(self):
        self.user.last_relapse_at = timezone.now() - timedelta(hours=2)
        self.assertEqual(self.user.current_streak_days(), 0)

    def test_log_relapse_banks_record_and_resets(self):
        self.user.date_joined = timezone.now() - timedelta(days=10)
        self.user.save()
        self.user.log_relapse()
        self.user.refresh_from_db()
        self.assertEqual(self.user.longest_streak_days, 10)
        self.assertEqual(self.user.current_streak_days(), 0)

    def test_log_relapse_keeps_existing_record(self):
        self.user.longest_streak_days = 30
        self.user.last_relapse_at = timezone.now() - timedelta(days=3)
        self.user.save()
        self.user.log_relapse()
        self.user.refresh_from_db()
        self.assertEqual(self.user.longest_streak_days, 30)


class AuthTests(TestCase):
    def test_pages_require_login(self):
        for name in ["home", "checkin", "journal", "study"]:
            response = self.client.get(reverse(name))
            self.assertRedirects(response, f"{reverse('login')}?next={reverse(name)}")

    def test_signup_logs_in(self):
        response = self.client.post(
            reverse("signup"),
            {"name": "Sam", "email": "sam@example.com", "password1": "steady-path-42", "password2": "steady-path-42"},
        )
        self.assertRedirects(response, reverse("home"))
        response = self.client.get(reverse("home"))
        self.assertContains(response, "Sam")

    def test_login_with_email(self):
        User.objects.create_user(email="b@example.com", password="steady-path-42")
        response = self.client.post(reverse("login"), {"username": "b@example.com", "password": "steady-path-42"})
        self.assertRedirects(response, reverse("home"))

    def test_password_reset_pages_render(self):
        self.assertContains(self.client.get(reverse("password_reset")), "Send reset link")


class CheckinTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="c@example.com", password="pw-long-enough-1")
        self.user.date_joined = timezone.now() - timedelta(days=4)
        self.user.save()
        self.client.force_login(self.user)

    def test_clean_checkin_saves_and_updates_in_place(self):
        self.client.post(reverse("checkin"), {"status": "clean", "mood": 4, "note": "Good day"})
        self.client.post(reverse("checkin"), {"status": "clean", "mood": 5, "note": "Even better"})
        entry = Checkin.objects.get(user=self.user)
        self.assertEqual((entry.mood, entry.note), (5, "Even better"))

    def test_relapse_needs_confirmation(self):
        response = self.client.post(reverse("checkin"), {"status": "relapse"})
        self.assertContains(response, "Confirm and save")
        self.assertFalse(Checkin.objects.exists())

        self.client.post(reverse("checkin"), {"status": "relapse", "confirm": "1"})
        self.user.refresh_from_db()
        self.assertEqual(Checkin.objects.get().status, "relapse")
        self.assertEqual(self.user.longest_streak_days, 4)
        self.assertEqual(self.user.current_streak_days(), 0)

    def test_editing_an_existing_relapse_does_not_log_again(self):
        self.client.post(reverse("checkin"), {"status": "relapse", "confirm": "1"})
        self.user.refresh_from_db()
        first_relapse = self.user.last_relapse_at

        response = self.client.post(reverse("checkin"), {"status": "relapse", "note": "more detail"})
        self.assertRedirects(response, reverse("home"))
        self.user.refresh_from_db()
        self.assertEqual(self.user.last_relapse_at, first_relapse)

    def test_journal_only_shows_own_entries(self):
        other = User.objects.create_user(email="other@example.com", password="pw-long-enough-1")
        Checkin.objects.create(user=other, day=timezone.localdate(), status="clean", note="not yours")
        Checkin.objects.create(user=self.user, day=timezone.localdate(), status="clean", note="mine")
        response = self.client.get(reverse("journal"))
        self.assertContains(response, "mine")
        self.assertNotContains(response, "not yours")


class StudyTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="d@example.com", password="pw-long-enough-1")
        self.client.force_login(self.user)

    def test_plan_starts_at_day_one(self):
        response = self.client.get(reverse("study"))
        self.assertContains(response, "Start day 1")
        self.assertContains(response, "Built on the rock")

    def test_completing_a_day_moves_plan_forward(self):
        response = self.client.post(
            reverse("study_detail", args=["built-on-the-rock"]), {"reflection": "Build on what lasts."}
        )
        self.assertRedirects(response, reverse("study"))
        entry = StudyEntry.objects.get(user=self.user)
        self.assertEqual(entry.reflection, "Build on what lasts.")
        self.assertContains(self.client.get(reverse("study")), "Continue with day 2")
        self.assertContains(self.client.get(reverse("home")), "Remain in the vine")

    def test_resaving_updates_the_same_entry(self):
        url = reverse("study_detail", args=["built-on-the-rock"])
        self.client.post(url, {"reflection": "First"})
        self.client.post(url, {"reflection": "Second"})
        self.assertEqual(StudyEntry.objects.get(user=self.user).reflection, "Second")

    def test_reflections_are_private(self):
        other = User.objects.create_user(email="o@example.com", password="pw-long-enough-1")
        StudyEntry.objects.create(user=other, slug="built-on-the-rock", reflection="not yours")
        response = self.client.get(reverse("study_detail", args=["built-on-the-rock"]))
        self.assertNotContains(response, "not yours")
        self.assertContains(response, "Mark day 1 complete")

    def test_unknown_study_is_404(self):
        self.assertEqual(self.client.get(reverse("study_detail", args=["nope"])).status_code, 404)


class MilestoneTests(TestCase):
    def test_progress_between_milestones(self):
        from .views import milestone_progress

        self.assertEqual(milestone_progress(0)["next"], 1)
        progress = milestone_progress(10)
        self.assertEqual((progress["next"], progress["days_left"], progress["percent"]), (14, 4, 43))

    def test_progress_after_a_year(self):
        from .views import milestone_progress

        progress = milestone_progress(400)
        self.assertEqual((progress["next"], progress["days_left"]), (730, 330))

    def test_home_renders_week_and_trail(self):
        user = User.objects.create_user(email="e@example.com", password="pw-long-enough-1")
        Checkin.objects.create(user=user, day=timezone.localdate(), status="clean")
        self.client.force_login(user)
        response = self.client.get(reverse("home"))
        self.assertContains(response, "1/7 checked in")
        self.assertContains(response, "The climb")


class SessionTests(TestCase):
    def test_sign_in_persists_for_a_year_and_renews(self):
        User.objects.create_user(email="f@example.com", password="steady-path-42")
        response = self.client.post(reverse("login"), {"username": "f@example.com", "password": "steady-path-42"})
        cookie = response.cookies["sessionid"]
        self.assertEqual(cookie["max-age"], 60 * 60 * 24 * 365)
        # Any later visit sends a refreshed cookie, pushing the expiry forward.
        self.assertIn("sessionid", self.client.get(reverse("home")).cookies)


class InstallableAppTests(TestCase):
    def test_manifest_opens_on_home(self):
        response = self.client.get(reverse("manifest"))
        self.assertEqual(response["Content-Type"], "application/manifest+json")
        data = response.json()
        self.assertEqual((data["start_url"], data["scope"], data["display"]), ("/", "/", "standalone"))
        self.assertEqual(len(data["icons"]), 3)

    def test_pages_link_the_manifest_and_icon(self):
        response = self.client.get(reverse("login"))
        self.assertContains(response, 'rel="manifest"')
        self.assertContains(response, 'rel="apple-touch-icon"')
