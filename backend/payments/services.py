from django.db import transaction
from rest_framework.exceptions import NotFound, ValidationError

from catalog.models import Product
from orders.models import Order
from payments.models import Payment

APPROVED_CARD_NUMBER = "4111111111111111"
REJECTED_CARD_NUMBER = "4000000000000002"
SIMULATED_PROVIDER = "pasarela-simulada"


def determine_payment_status(card_number):
    if card_number == APPROVED_CARD_NUMBER:
        return Payment.Status.APPROVED
    if card_number == REJECTED_CARD_NUMBER:
        return Payment.Status.REJECTED
    return Payment.Status.PENDING


@transaction.atomic
def create_payment(user, order_id, card_number):
    try:
        order = Order.objects.select_for_update().get(pk=order_id, user=user)
    except Order.DoesNotExist as error:
        raise NotFound({"pedido": "El pedido no existe."}) from error
    if order.status == Order.Status.CANCELED:
        raise ValidationError({"pedido": "Un pedido cancelado no se puede pagar."})
    if Payment.objects.filter(order=order).exists():
        raise ValidationError({"pedido": "El pedido ya tiene un pago."})

    payment_status = determine_payment_status(card_number)
    payment = Payment.objects.create(
        order=order,
        status=payment_status,
        amount=order.total,
        provider=SIMULATED_PROVIDER,
        card_last_four=card_number[-4:],
    )

    if payment_status == Payment.Status.APPROVED:
        order.status = Order.Status.CONFIRMED
        order.save(update_fields=("status", "updated_at"))

    return payment


@transaction.atomic
def refund_payment(payment):
    locked_payment = Payment.objects.select_for_update().get(pk=payment.pk)
    order = Order.objects.select_for_update().get(pk=locked_payment.order_id)
    if locked_payment.status != Payment.Status.APPROVED:
        raise ValidationError({"estado": "Solo se pueden reembolsar pagos aprobados."})

    if order.status != Order.Status.CANCELED:
        order_items = list(order.items.all().order_by("product_id"))
        product_ids = [item.product_id for item in order_items if item.product_id]
        products = {
            product.pk: product
            for product in Product.objects.select_for_update()
            .filter(pk__in=product_ids)
            .order_by("pk")
        }

        for item in order_items:
            product = products.get(item.product_id)
            if product is not None:
                product.stock += item.quantity
                product.save(update_fields=("stock", "updated_at"))

        order.status = Order.Status.CANCELED
        order.save(update_fields=("status", "updated_at"))

    locked_payment.status = Payment.Status.REFUNDED
    locked_payment.save(update_fields=("status", "updated_at"))
    return locked_payment
