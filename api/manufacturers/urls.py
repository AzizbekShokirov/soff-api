from django.urls import path
from .views import ManufacturerView, ManufacturerDetailView

urlpatterns = [
    path('', ManufacturerView.as_view(), name='manufacturer-list'),
    path('<int:category_id>', ManufacturerDetailView.as_view(), name='manufacturer-detail'),
]
