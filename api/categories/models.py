from django.db import models


class RoomCategory(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(
        upload_to="images/room_categories/", null=True, blank=True
    )
    slug = models.SlugField(unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Room category"
        verbose_name_plural = "Room categories"

    def __str__(self):
        return self.name


class ProductCategory(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(
        upload_to="images/product_categories/", null=True, blank=True
    )
    slug = models.SlugField(unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Product category"
        verbose_name_plural = "Product categories"

    def __str__(self):
        return self.name
