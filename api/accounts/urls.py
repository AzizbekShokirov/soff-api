from django.urls import path

from rest_framework_simplejwt.views import TokenRefreshView
from accounts.views import (
    ConfirmEmailView,
    FavoriteView,
    FavoriteDetailView,
    LoginView,
    LogoutView,
    OTPResendView,
    OTPValidateView,
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
    path("token/refresh", TokenRefreshView.as_view(), name="token-refresh"),
    path("otp/resend", OTPResendView.as_view(), name="otp-resend"),
    path("otp/verify", OTPValidateView.as_view(), name="otp-verify"),
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
    path("profile", ProfileView.as_view(), name="profile"),
    path("favorites", FavoriteView.as_view(), name="favorites"),
    path(
        "favorites/<slug:product_slug>",
        FavoriteDetailView.as_view(),
        name="favorites-detail",
    ),
]
