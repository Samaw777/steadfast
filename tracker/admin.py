from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Checkin, UrgeLog, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ["email"]
    list_display = ["email", "name", "longest_streak_days", "last_relapse_at", "is_staff"]
    search_fields = ["email", "name"]
    fieldsets = [
        (None, {"fields": ["email", "password"]}),
        ("Profile", {"fields": ["name", "last_relapse_at", "longest_streak_days"]}),
        ("Permissions", {"fields": ["is_active", "is_staff", "is_superuser", "groups", "user_permissions"]}),
        ("Dates", {"fields": ["last_login", "date_joined"]}),
    ]
    add_fieldsets = [
        (None, {"classes": ["wide"], "fields": ["email", "name", "password1", "password2"]}),
    ]


@admin.register(Checkin)
class CheckinAdmin(admin.ModelAdmin):
    list_display = ["user", "day", "status", "mood"]
    list_filter = ["status"]


@admin.register(UrgeLog)
class UrgeLogAdmin(admin.ModelAdmin):
    list_display = ["user", "outcome", "created_at"]
    list_filter = ["outcome"]
