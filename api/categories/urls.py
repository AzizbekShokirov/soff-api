from django.urls import path
from .views import (
    RoomCategoryView,
    RoomCategoryDetailView,
    ProductCategoryView,
    ProductCategoryDetailView,
)

urlpatterns = [
    path('room', RoomCategoryView.as_view(), name='room-category-list'),
    path('room/<int:category_id>', RoomCategoryDetailView.as_view(), name='room-category-detail'),
    path('product', ProductCategoryView.as_view(), name='product-category-list'),
    path('product/<int:category_id>', ProductCategoryDetailView.as_view(), name='product-category-detail'),
]
