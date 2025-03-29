from django.urls import path

from .views import ProductCategoryDetailView, ProductCategoryView, RoomCategoryDetailView, RoomCategoryView

urlpatterns = [
    path("room", RoomCategoryView.as_view(), name="room-category-list"),
    path(
        "room/<slug:slug>",
        RoomCategoryDetailView.as_view(),
        name="room-category-detail",
    ),
    path("product", ProductCategoryView.as_view(), name="product-category-list"),
    path(
        "product/<slug:slug>",
        ProductCategoryDetailView.as_view(),
        name="product-category-detail",
    ),
]
