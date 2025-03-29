from django.contrib import admin

from .models import Manufacturer


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "description",
        "image",
        "slug",
        "id",
        "created_at",
        "updated_at",
    )
    search_fields = ("name",)
    list_filter = ("created_at", "updated_at")
    prepopulated_fields = {"slug": ("name",)}
