from django.urls import path

from products.views import (
    ProductDetailView,
    ProductLikeView,
    ProductSearchView,
    ProductView,
)

urlpatterns = [
    path("", ProductView.as_view(), name="products-list"),
    path("<slug:product_slug>", ProductDetailView.as_view(), name="product-detail"),
    path("like/<slug:product_slug>", ProductLikeView.as_view(), name="product-like"),
    path("search/", ProductSearchView.as_view(), name="search-products"),
]
