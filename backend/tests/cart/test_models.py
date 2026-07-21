from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from cart.models import Cart, CartItem


@pytest.mark.django_db
def test_only_one_active_cart_is_allowed_per_user(user):
    Cart.objects.create(user=user, active=True)

    with pytest.raises(IntegrityError), transaction.atomic():
        Cart.objects.create(user=user, active=True)


@pytest.mark.django_db
def test_product_cannot_be_duplicated_in_same_cart(user, product_factory):
    cart = Cart.objects.create(user=user)
    product = product_factory()
    CartItem.objects.create(cart=cart, product=product, quantity=1)

    with pytest.raises(IntegrityError), transaction.atomic():
        CartItem.objects.create(cart=cart, product=product, quantity=2)


@pytest.mark.django_db
def test_cart_item_quantity_must_be_positive(user, product_factory):
    item = CartItem(
        cart=Cart.objects.create(user=user),
        product=product_factory(),
        quantity=0,
    )

    with pytest.raises(ValidationError) as error:
        item.full_clean()

    assert "quantity" in error.value.message_dict


@pytest.mark.django_db
def test_model_calculations_use_decimal(user, product_factory):
    cart = Cart.objects.create(user=user)
    first_product = product_factory(price=Decimal("2.50"))
    second_product = product_factory(price=Decimal("1.25"))
    first_item = CartItem.objects.create(
        cart=cart,
        product=first_product,
        quantity=2,
    )
    CartItem.objects.create(
        cart=cart,
        product=second_product,
        quantity=4,
    )

    assert first_item.subtotal == Decimal("5.00")
    assert cart.total_items == 6
    assert cart.total == Decimal("10.00")
