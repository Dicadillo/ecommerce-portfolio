from django.db import transaction
from django.db.models import Prefetch
from rest_framework.exceptions import ValidationError

from cart.models import Cart, CartItem
from catalog.models import Product


def get_active_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user, active=True)
    return cart


def get_cart_with_items(cart):
    items = CartItem.objects.select_related("product").order_by("id")
    return Cart.objects.prefetch_related(Prefetch("items", queryset=items)).get(
        pk=cart.pk
    )


def validate_product(product, quantity):
    if not product.active:
        raise ValidationError({"producto": "El producto no está activo."})
    if quantity > product.stock:
        raise ValidationError({"cantidad": "La cantidad supera el stock disponible."})


@transaction.atomic
def add_product(cart, product, quantity):
    locked_cart = Cart.objects.select_for_update().get(pk=cart.pk)
    locked_product = Product.objects.select_for_update().get(pk=product.pk)
    item = (
        CartItem.objects.select_for_update()
        .filter(cart=locked_cart, product=locked_product)
        .first()
    )
    resulting_quantity = quantity if item is None else item.quantity + quantity
    validate_product(locked_product, resulting_quantity)

    if item is None:
        item = CartItem.objects.create(
            cart=locked_cart,
            product=locked_product,
            quantity=resulting_quantity,
        )
        created = True
    else:
        item.quantity = resulting_quantity
        item.save(update_fields=("quantity", "updated_at"))
        created = False

    return item, created


@transaction.atomic
def update_item_quantity(item, quantity):
    locked_item = (
        CartItem.objects.select_for_update().select_related("product").get(pk=item.pk)
    )
    locked_product = Product.objects.select_for_update().get(pk=locked_item.product_id)
    if quantity > locked_product.stock:
        raise ValidationError({"cantidad": "La cantidad supera el stock disponible."})

    locked_item.product = locked_product
    locked_item.quantity = quantity
    locked_item.save(update_fields=("quantity", "updated_at"))
    return locked_item
