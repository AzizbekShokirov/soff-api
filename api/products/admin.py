from django.contrib import admin

from products.models import Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "price",
        "room_category",
        "product_category",
        "slug",
        "id",
        "created_at",
        "updated_at",
    )
    search_fields = ["title", "room_category", "product_category", "slug"]
    list_filter = ["room_category", "product_category"]
    prepopulated_fields = {"slug": ("title",)}
    ordering = ["id", "title", "price", "room_category", "product_category", "slug"]
    inlines = [ProductImageInline]


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ["image", "product", "id"]
    search_fields = ["product"]
    list_filter = ["product"]
    ordering = ["product", "image", "id"]
