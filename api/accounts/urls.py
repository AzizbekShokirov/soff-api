from django.urls import path

from .views import (
    ConfirmEmailView,
    FavoriteView,
    LoginView,
    LogoutView,
    OTPResendView,
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetView,
    ProfileView,
    RegisterView,
)

app_name = "accounts"

urlpatterns = [
    path("register", RegisterView.as_view(), name="register"),
    path(
        "register/confirm",
        ConfirmEmailView.as_view(),
        name="confirm-email",
    ),
    path("login", LoginView.as_view(), name="login"),
    path("logout", LogoutView.as_view(), name="logout"),
    path("profile", ProfileView.as_view(), name="profile"),
    path("password/change", PasswordChangeView.as_view(), name="password-change"),
    path(
        "password/reset",
        PasswordResetView.as_view(),
        name="password-reset-request",
    ),
    path(
        "password/reset/confirm",
        PasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
    path("favorites", FavoriteView.as_view(), name="favorites"),
    path("otp/resend", OTPResendView.as_view(), name="otp-resend"),
]
