from django.contrib import admin

from .models import ProductCategory, RoomCategory

@admin.register(RoomCategory)
class RoomCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'created_at', 'updated_at')
    search_fields = ('name', 'slug')
    ordering = ('id', 'name')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'created_at', 'updated_at')
    search_fields = ('name', 'slug')
    ordering = ('id', 'name')
    prepopulated_fields = {'slug': ('name',)}
