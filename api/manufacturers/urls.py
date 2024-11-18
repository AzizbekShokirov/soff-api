from django.urls import path

from manufacturers.views import ManufacturerDetailView, ManufacturerView

urlpatterns = [
    path("", ManufacturerView.as_view(), name="manufacturer-list"),
    path("<slug:slug>", ManufacturerDetailView.as_view(), name="manufacturer-detail"),
]
