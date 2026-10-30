from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Checkin, UrgeLog, User


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
        for name in ["home", "checkin", "journal", "urge"]:
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


class UrgeTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="d@example.com", password="pw-long-enough-1")
        self.client.force_login(self.user)

    def test_resisted_is_logged(self):
        response = self.client.post(reverse("urge"), {"outcome": "resisted"})
        self.assertContains(response, "That took strength")
        self.assertEqual(UrgeLog.objects.get().outcome, "resisted")

    def test_relapsed_needs_confirmation_then_resets_streak(self):
        self.client.post(reverse("urge"), {"outcome": "relapsed"})
        self.assertFalse(UrgeLog.objects.exists())

        response = self.client.post(reverse("urge"), {"outcome": "relapsed", "confirm": "1"})
        self.assertContains(response, "Tomorrow is")
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.last_relapse_at)


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
