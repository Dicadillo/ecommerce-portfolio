import uuid
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from orders.models import Order


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pendiente", "Pendiente"
        APPROVED = "aprobado", "Aprobado"
        REJECTED = "rechazado", "Rechazado"
        REFUNDED = "reembolsado", "Reembolsado"

    order = models.OneToOneField(
        Order,
        on_delete=models.PROTECT,
        related_name="payment",
    )
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.PENDING,
    )
    amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    reference = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    provider = models.CharField(max_length=80, default="pasarela-simulada")
    card_last_four = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at", "-id")
        constraints = (
            models.CheckConstraint(
                condition=models.Q(amount__gte=0),
                name="payments_payment_amount_non_negative",
            ),
        )

    def __str__(self):
        return f"Payment {self.reference} - {self.status}"
