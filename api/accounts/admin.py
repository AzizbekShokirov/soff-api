from django.contrib import admin

from .models import Favorite, User, UserOTP


class UserOTPInline(admin.TabularInline):
    model = UserOTP
    extra = 0


class FavoriteInline(admin.TabularInline):
    model = Favorite
    extra = 0


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
        "date_joined",
    )
    search_fields = ("email", "first_name", "last_name", "is_active", "is_staff")
    list_filter = ("is_active", "is_staff", "date_joined")
    ordering = (
        "id",
        "email",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
        "date_joined",
    )
    readonly_fields = ("id", "date_joined")
    inlines = [UserOTPInline, FavoriteInline]


@admin.register(UserOTP)
class UserOTPAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "otp",
        "otp_attempts",
        "is_blocked",
        "expires_at",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "user",
        "otp",
        "otp_attempts",
        "is_blocked",
        "expires_at",
        "created_at",
        "updated_at",
    )
    list_filter = ("otp_attempts", "is_blocked", "expires_at")
    ordering = (
        "id",
        "user",
        "otp",
        "otp_attempts",
        "created_at",
        "is_blocked",
        "expires_at",
    )
    readonly_fields = ("id", "created_at", "expires_at")


@admin.register(Favorite)
class FavoritesAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "liked", "id", "created_at", "updated_at")
    search_fields = ("user", "product", "liked")
    list_filter = ("user", "liked")
    ordering = ("id", "user", "product", "liked")
    readonly_fields = ("id", "created_at", "updated_at")
