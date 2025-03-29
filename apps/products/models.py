from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.categories.models import ProductCategory, RoomCategory
from apps.manufacturers.models import Manufacturer


class Product(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    color = models.CharField(max_length=100)
    material = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    length = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    width = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    height = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    maximum_load = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
    )
    room_category = models.ForeignKey(RoomCategory, on_delete=models.CASCADE, related_name="products")
    product_category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name="products")
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE, related_name="products")
    is_ar = models.BooleanField(default=False)
    ar_model = models.URLField(max_length=200, blank=True, null=True)
    ar_url = models.URLField(max_length=200, blank=True, null=True)
    slug = models.SlugField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return self.title


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="images/products")

    class Meta:
        verbose_name = "Product Image"
        verbose_name_plural = "Product Images"

    def __str__(self):
        return f"{self.product.title} image with ID: {self.pk}"
