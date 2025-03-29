from django.db import models

from apps.products.models import Product
from apps.users.models import User


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Cart"
        verbose_name_plural = "Carts"

    def total_cost(self):
        return sum(item.total_price() for item in self.cart_items.all())

    def __str__(self):
        return f"{self.user.email}'s cart"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name="cart_items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cart Item"
        verbose_name_plural = "Cart Items"
        ordering = ["-created_at"]

    def total_price(self):
        return self.quantity * self.product.price

    def __str__(self):
        return f"{self.product.title} ({self.quantity})"
