from django.db import models


class Manufacturer(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to="images/manufacturers/", blank=True, null=True)
    slug = models.SlugField(max_length=100, unique=True)
    instagram_url = models.URLField(max_length=200, blank=True, null=True)
    telegram_url = models.URLField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Manufacturer"
        verbose_name_plural = "Manufacturers"

    def __str__(self):
        return self.name
