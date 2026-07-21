from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from cart.models import Cart, CartItem
from tests.assertions import assert_error_response
from tests.cart.conftest import authenticate_client


def add_product(client, product, quantity=1):
    return client.post(
        reverse("cart-item-list"),
        {"producto": product.id, "cantidad": quantity},
        format="json",
    )


@pytest.mark.django_db
def test_empty_cart(authenticated_client, user):
    response = authenticated_client.get(reverse("cart-detail"))

    assert response.status_code == 200
    assert response.data["articulos"] == []
    assert response.data["cantidad_total"] == 0
    assert response.data["total"] == "0.00"
    assert Cart.objects.filter(user=user, active=True).count() == 1


@pytest.mark.django_db
def test_add_product(authenticated_client, user, product_factory):
    product = product_factory(price=Decimal("12.50"), stock=5)

    response = add_product(authenticated_client, product, quantity=2)

    assert response.status_code == 201
    assert response.data == {
        "id": response.data["id"],
        "producto": product.id,
        "cantidad": 2,
        "subtotal": "25.00",
    }
    item = CartItem.objects.get(cart__user=user, product=product)
    assert item.quantity == 2


@pytest.mark.django_db
def test_add_same_product_twice_increments_quantity(
    authenticated_client,
    user,
    product_factory,
):
    product = product_factory(stock=8)

    first_response = add_product(authenticated_client, product, quantity=2)
    second_response = add_product(authenticated_client, product, quantity=3)

    assert first_response.status_code == 201
    assert second_response.status_code == 200
    assert second_response.data["cantidad"] == 5
    assert CartItem.objects.filter(cart__user=user, product=product).count() == 1


@pytest.mark.django_db
def test_update_quantity(authenticated_client, user, product_factory):
    product = product_factory(stock=6)
    item_id = add_product(authenticated_client, product).data["id"]

    response = authenticated_client.patch(
        reverse("cart-item-detail", args=[item_id]),
        {"cantidad": 4},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["cantidad"] == 4
    assert CartItem.objects.get(cart__user=user, product=product).quantity == 4


@pytest.mark.django_db
def test_delete_item(authenticated_client, user, product_factory):
    item_id = add_product(authenticated_client, product_factory()).data["id"]

    response = authenticated_client.delete(reverse("cart-item-detail", args=[item_id]))

    assert response.status_code == 204
    assert not CartItem.objects.filter(pk=item_id, cart__user=user).exists()


@pytest.mark.django_db
def test_clear_cart(authenticated_client, user, product_factory):
    add_product(authenticated_client, product_factory())
    add_product(authenticated_client, product_factory())

    response = authenticated_client.delete(reverse("cart-clear"))

    assert response.status_code == 204
    assert not CartItem.objects.filter(cart__user=user).exists()


@pytest.mark.django_db
def test_add_nonexistent_product(authenticated_client):
    response = authenticated_client.post(
        reverse("cart-item-list"),
        {"producto": 999999, "cantidad": 1},
        format="json",
    )

    assert response.status_code == 400
    assert_error_response(response, "validacion_incorrecta", "producto")


@pytest.mark.django_db
def test_add_inactive_product(authenticated_client, product_factory):
    product = product_factory(active=False)

    response = add_product(authenticated_client, product)

    assert response.status_code == 400
    assert_error_response(response, "regla_de_negocio", "producto")


@pytest.mark.django_db
@pytest.mark.parametrize("quantity", (0, -1))
def test_add_zero_or_negative_quantity(
    quantity,
    authenticated_client,
    product_factory,
):
    response = add_product(authenticated_client, product_factory(), quantity)

    assert response.status_code == 400
    assert_error_response(response, "validacion_incorrecta", "cantidad")


@pytest.mark.django_db
def test_add_quantity_above_stock(authenticated_client, product_factory):
    product = product_factory(stock=2)

    response = add_product(authenticated_client, product, quantity=3)

    assert response.status_code == 400
    assert_error_response(response, "regla_de_negocio", "cantidad")


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("method", "url_name", "args"),
    (
        ("get", "cart-detail", None),
        ("post", "cart-item-list", None),
        ("patch", "cart-item-detail", (1,)),
        ("delete", "cart-item-detail", (1,)),
        ("delete", "cart-clear", None),
    ),
)
def test_all_cart_endpoints_require_authentication(
    method,
    url_name,
    args,
    api_client,
):
    url = reverse(url_name, args=args)
    response = getattr(api_client, method)(url, {}, format="json")

    assert response.status_code == 401
    assert_error_response(response, "autenticacion_requerida")


@pytest.mark.django_db
def test_users_cannot_access_each_others_cart(
    user_factory,
    product_factory,
):
    owner = user_factory(username="owner")
    other_user = user_factory(username="other-user")
    owner_client = authenticate_client(APIClient(), owner)
    other_client = authenticate_client(APIClient(), other_user)
    item_id = add_product(owner_client, product_factory(), quantity=2).data["id"]

    cart_response = other_client.get(reverse("cart-detail"))
    update_response = other_client.patch(
        reverse("cart-item-detail", args=[item_id]),
        {"cantidad": 1},
        format="json",
    )
    delete_response = other_client.delete(reverse("cart-item-detail", args=[item_id]))

    assert cart_response.status_code == 200
    assert cart_response.data["articulos"] == []
    assert update_response.status_code == 404
    assert delete_response.status_code == 404
    assert_error_response(update_response, "recurso_no_encontrado")
    assert_error_response(delete_response, "recurso_no_encontrado")
    assert CartItem.objects.filter(pk=item_id, cart__user=owner).exists()


@pytest.mark.django_db
def test_cart_calculates_subtotals_quantity_and_total(
    authenticated_client,
    product_factory,
):
    first_product = product_factory(price=Decimal("10.50"), stock=5)
    second_product = product_factory(price=Decimal("4.25"), stock=5)
    add_product(authenticated_client, first_product, quantity=2)
    add_product(authenticated_client, second_product, quantity=3)

    response = authenticated_client.get(reverse("cart-detail"))

    subtotals = {
        item["producto"]: item["subtotal"] for item in response.data["articulos"]
    }
    assert response.status_code == 200
    assert subtotals == {
        first_product.id: "21.00",
        second_product.id: "12.75",
    }
    assert response.data["cantidad_total"] == 5
    assert response.data["total"] == "33.75"
