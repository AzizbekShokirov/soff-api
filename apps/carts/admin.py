from django.contrib import admin

from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "total_cost", "id")
    search_fields = ("user__email",)
    inlines = [CartItemInline]


# @admin.register(CartItem)
# class CartItemAdmin(admin.ModelAdmin):
#     list_display = (
#         "cart",
#         "product",
#         "quantity",
#         "total_price",
#         "id",
#         "created_at",
#         "updated_at",
#     )
#     search_fields = ("cart__user__email", "product__title")
