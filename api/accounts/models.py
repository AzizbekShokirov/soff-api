from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from accounts.managers import CustomUserManager
from products.models import Product


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    image = models.ImageField(upload_to="images/users", blank=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.email


class UserOTP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="otp")
    otp = models.IntegerField()
    otp_attempts = models.IntegerField(default=3)
    is_blocked = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_expired(self):
        return timezone.now() > self.expires_at

    def is_max_attempts_reached(self):
        return self.otp_attempts == 0

    def __str__(self):
        return f"{self.user.email} - {self.otp}"

    class Meta:
        verbose_name = "User OTP"
        verbose_name_plural = "User OTPs"


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorites")
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="favorites"
    )
    is_liked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "product") # User can like a product only once
        verbose_name = "Favorite"
        verbose_name_plural = "Favorites"

    def __str__(self):
        return f"{self.user.email} likes {self.product.title}"
