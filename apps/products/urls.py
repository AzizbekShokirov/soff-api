from django.urls import path

from .views import (
    ProductDetailView,
    ProductFilterView,
    ProductSearchView,
    ProductView,
)

urlpatterns = [
    path("", ProductView.as_view(), name="products-list"),
    path("<slug:product_slug>", ProductDetailView.as_view(), name="product-detail"),
    path("filter/", ProductFilterView.as_view(), name="filter-products"),
    path("search/", ProductSearchView.as_view(), name="search-products"),
]
