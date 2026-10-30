from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("checkin/", views.checkin, name="checkin"),
    path("journal/", views.journal, name="journal"),
    path("study/", views.study_index, name="study"),
    path("study/<slug:slug>/", views.study_detail, name="study_detail"),
    # Accounts
    path("signup/", views.signup, name="signup"),
    path("login/", auth_views.LoginView.as_view(redirect_authenticated_user=True), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("password-reset/", auth_views.PasswordResetView.as_view(), name="password_reset"),
    path("password-reset/sent/", auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path(
        "reset-password/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path("reset-password/done/", auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),
]
