from django.urls import path

from .views import (
    ProductView,
    ProductDetailView,
    ProductLikeView,
    ProductSearchView
)

urlpatterns = [
    path('', ProductView.as_view(), name="products"),
    path('<int:product_id>', ProductDetailView.as_view(), name="product_detail"),
    path('like/<int:product_id>', ProductLikeView.as_view(), name='product_like'),
    path('search/', ProductSearchView.as_view(), name='search_products'),
]
