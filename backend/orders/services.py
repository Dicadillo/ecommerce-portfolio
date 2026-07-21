from decimal import Decimal

from django.db import transaction

from cart.models import Cart, CartItem
from catalog.models import Product
from config.exceptions import BusinessRuleError
from orders.models import Order, OrderItem


def get_order_with_items(order):
    return Order.objects.prefetch_related("items").get(pk=order.pk)


@transaction.atomic
def create_order_from_cart(user, delivery_data):
    cart = Cart.objects.select_for_update().filter(user=user, active=True).first()
    if cart is None:
        raise BusinessRuleError({"carrito": "El carrito está vacío."})

    cart_items = list(
        CartItem.objects.select_for_update().filter(cart=cart).order_by("product_id")
    )
    if not cart_items:
        raise BusinessRuleError({"carrito": "El carrito está vacío."})

    product_ids = [item.product_id for item in cart_items]
    products = {
        product.pk: product
        for product in Product.objects.select_for_update()
        .filter(pk__in=product_ids)
        .order_by("pk")
    }

    for item in cart_items:
        product = products[item.product_id]
        if not product.active:
            raise BusinessRuleError(
                {"carrito": f"El producto '{product.name}' ya no está activo."}
            )
        if item.quantity > product.stock:
            raise BusinessRuleError(
                {
                    "carrito": (
                        f"No hay stock suficiente para el producto '{product.name}'."
                    )
                }
            )

    order = Order.objects.create(
        user=user,
        status=Order.Status.PENDING,
        **delivery_data,
    )
    total = Decimal("0.00")
    order_items = []

    for item in cart_items:
        product = products[item.product_id]
        subtotal = product.price * item.quantity
        total += subtotal
        order_items.append(
            OrderItem(
                order=order,
                product=product,
                product_name=product.name,
                unit_price=product.price,
                quantity=item.quantity,
                subtotal=subtotal,
            )
        )
        product.stock -= item.quantity
        product.save(update_fields=("stock", "updated_at"))

    OrderItem.objects.bulk_create(order_items)
    order.total = total
    order.save(update_fields=("total", "updated_at"))
    CartItem.objects.filter(pk__in=[item.pk for item in cart_items]).delete()
    return get_order_with_items(order)


@transaction.atomic
def cancel_order(order):
    locked_order = Order.objects.select_for_update().get(pk=order.pk)
    cancelable_statuses = (Order.Status.PENDING, Order.Status.CONFIRMED)
    if locked_order.status not in cancelable_statuses:
        raise BusinessRuleError(
            {"estado": "El pedido no se puede cancelar en su estado actual."}
        )

    order_items = list(locked_order.items.all().order_by("product_id"))
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

    locked_order.status = Order.Status.CANCELED
    locked_order.save(update_fields=("status", "updated_at"))
    return get_order_with_items(locked_order)
