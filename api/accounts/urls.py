from django.urls import path

from accounts.views import (
    ConfirmEmailView,
    FavoriteView,
    # FavoriteDetailView,
    LoginView,
    LogoutView,
    OTPResendView,
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetView,
    ProfileView,
    RegisterView,
    TokenRefreshView,
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
    path("otp/resend", OTPResendView.as_view(), name="otp-resend"),
    path("token/refresh", TokenRefreshView.as_view(), name="token-refresh"),
    path("favorites", FavoriteView.as_view(), name="favorites"),
    # path("favorites/<slug:product_slug>", FavoriteDetailView.as_view(), name="favorites-detail"),
]
