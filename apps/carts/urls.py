from django.urls import path

from .views import CartDetailView, CartView, ClearCartView

urlpatterns = [
    path("item", CartView.as_view(), name="carts-list"),
    path("item/<slug:product_slug>", CartDetailView.as_view(), name="update-cart-item"),
    path("clear", ClearCartView.as_view(), name="clear-cart"),
]
