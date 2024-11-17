from django.urls import path

from .views import (
    ProductView,
    ProductDetailView,
    ProductLikeView,
    ProductSearchView
)

urlpatterns = [
    path('', ProductView.as_view(), name="products-list"),
    path('<int:product_id>', ProductDetailView.as_view(), name="product-detail"),
    path('like/<int:product_id>', ProductLikeView.as_view(), name='product-like'),
    path('search/', ProductSearchView.as_view(), name='search-products'),
]
