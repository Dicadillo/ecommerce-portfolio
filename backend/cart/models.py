from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from catalog.models import Product


class Cart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="carts",
    )
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at", "-id")
        constraints = (
            models.UniqueConstraint(
                fields=("user",),
                condition=models.Q(active=True),
                name="cart_unique_active_cart_per_user",
            ),
        )

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def total(self):
        return sum(
            (item.subtotal for item in self.items.all()),
            start=Decimal("0.00"),
        )

    def __str__(self):
        state = "active" if self.active else "inactive"
        return f"Cart {self.pk} - {self.user} ({state})"


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="cart_items",
    )
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("id",)
        constraints = (
            models.UniqueConstraint(
                fields=("cart", "product"),
                name="cart_unique_product_per_cart",
            ),
            models.CheckConstraint(
                condition=models.Q(quantity__gt=0),
                name="cart_item_quantity_greater_than_zero",
            ),
        )

    @property
    def subtotal(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.product} x {self.quantity}"
