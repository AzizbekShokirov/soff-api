from django.contrib import admin

from accounts.models import Favorite, User, UserOTP


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
        "id",
        "phone_number",
        "image",
        "date_joined",
        "last_login",
    )
    search_fields = ("email", "first_name", "last_name")
    list_filter = ("is_active", "is_staff", "date_joined", "last_login")
    ordering = (
        "email",
        "id",
        "first_name",
        "last_name",
    )
    readonly_fields = ("id", "date_joined", "last_login")
    inlines = [UserOTPInline, FavoriteInline]


@admin.register(UserOTP)
class UserOTPAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "otp",
        "otp_attempts",
        "is_blocked",
        "created_at",
        "updated_at",
        "expires_at",
    )
    search_fields = ("user",)
    list_filter = ("otp_attempts", "is_blocked", "expires_at")
    ordering = ("user", "otp_attempts")
    readonly_fields = ("id", "created_at", "expires_at", "updated_at")


@admin.register(Favorite)
class FavoritesAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "liked", "id", "created_at", "updated_at")
    search_fields = ("user", "product", "liked")
    list_filter = ("user", "liked")
    ordering = ("id", "user", "product", "liked")
    readonly_fields = ("id", "created_at", "updated_at")
