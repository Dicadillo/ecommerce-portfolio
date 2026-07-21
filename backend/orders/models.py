from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from catalog.models import Product


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pendiente", "Pendiente"
        CONFIRMED = "confirmado", "Confirmado"
        SHIPPED = "enviado", "Enviado"
        DELIVERED = "entregado", "Entregado"
        CANCELED = "cancelado", "Cancelado"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders",
    )
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.PENDING,
    )
    recipient_name = models.CharField(max_length=200)
    address = models.TextField()
    city = models.CharField(max_length=120)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    total = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at", "-id")
        constraints = (
            models.CheckConstraint(
                condition=models.Q(total__gte=0),
                name="orders_order_total_non_negative",
            ),
        )

    def __str__(self):
        return f"Order {self.pk} - {self.user}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_items",
    )
    product_name = models.CharField(max_length=180)
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    subtotal = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    class Meta:
        ordering = ("id",)
        constraints = (
            models.CheckConstraint(
                condition=models.Q(unit_price__gte=0),
                name="orders_item_unit_price_non_negative",
            ),
            models.CheckConstraint(
                condition=models.Q(quantity__gt=0),
                name="orders_item_quantity_greater_than_zero",
            ),
            models.CheckConstraint(
                condition=models.Q(subtotal__gte=0),
                name="orders_item_subtotal_non_negative",
            ),
        )

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"
