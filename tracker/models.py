from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("An email address is required.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """An account signs in with its email and carries its own streak state."""

    username = None
    first_name = None
    last_name = None
    email = models.EmailField("email address", unique=True)
    name = models.CharField(max_length=100, blank=True)

    # Null until the first slip; the streak then counts from here instead of date_joined.
    last_relapse_at = models.DateTimeField(null=True, blank=True)
    longest_streak_days = models.PositiveIntegerField(default=0)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

    @property
    def display_name(self):
        return self.name or self.email.split("@")[0]

    @property
    def streak_reference(self):
        return self.last_relapse_at or self.date_joined

    def current_streak_days(self, now=None):
        """Whole days since the last slip (or since sign-up). A slip today means 0."""
        now = now or timezone.now()
        return max(0, (now - self.streak_reference).days)

    def log_relapse(self, now=None):
        """Bank the streak that just ended if it's a record, then restart the clock."""
        now = now or timezone.now()
        self.longest_streak_days = max(self.longest_streak_days, self.current_streak_days(now))
        self.last_relapse_at = now
        self.save(update_fields=["longest_streak_days", "last_relapse_at"])


class Checkin(models.Model):
    """One per account per day. Doubles as the journal."""

    class Status(models.TextChoices):
        CLEAN = "clean", "Steady"
        RELAPSE = "relapse", "Slipped"

    class Mood(models.IntegerChoices):
        STRUGGLING = 1, "Struggling"
        LOW = 2, "Low"
        OKAY = 3, "Okay"
        GOOD = 4, "Good"
        GREAT = 5, "Great"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="checkins")
    day = models.DateField()
    status = models.CharField(max_length=10, choices=Status.choices)
    mood = models.PositiveSmallIntegerField(
        choices=Mood.choices,
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-day"]
        constraints = [
            models.UniqueConstraint(fields=["user", "day"], name="one_checkin_per_day"),
        ]

    def __str__(self):
        return f"{self.user} — {self.day} ({self.status})"


class UrgeLog(models.Model):
    class Outcome(models.TextChoices):
        RESISTED = "resisted", "Resisted"
        RELAPSED = "relapsed", "Relapsed"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="urge_logs")
    outcome = models.CharField(max_length=10, choices=Outcome.choices)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} — {self.outcome} at {self.created_at:%Y-%m-%d %H:%M}"
