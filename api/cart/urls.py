from django.urls import path

from .views import CartView, ClearCartView, CartDetailView

urlpatterns = [
    path("items/", CartView.as_view(), name="cart"),
    path("item/<int:item_id>/", CartDetailView.as_view(), name="update-cart-item"),
    path("clear/", ClearCartView.as_view(), name="clear-cart"),
]
