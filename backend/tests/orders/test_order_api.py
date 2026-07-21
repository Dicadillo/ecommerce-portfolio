from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from cart.models import Cart, CartItem
from orders.models import Order, OrderItem
from tests.assertions import assert_error_response
from tests.orders.conftest import authenticate_client


def delivery_payload(**overrides):
    values = {
        "nombre_destinatario": "Ada Lovelace",
        "direccion": "Calle Principal 42",
        "ciudad": "Madrid",
        "codigo_postal": "28001",
        "pais": "España",
    }
    values.update(overrides)
    return values


def add_cart_item(user, product, quantity=1):
    cart, _ = Cart.objects.get_or_create(user=user, active=True)
    return CartItem.objects.create(
        cart=cart,
        product=product,
        quantity=quantity,
    )


def checkout(client, **overrides):
    return client.post(
        reverse("order-list-create"),
        delivery_payload(**overrides),
        format="json",
    )


def create_order_record(user, product, status=Order.Status.CONFIRMED, quantity=2):
    subtotal = product.price * quantity
    order = Order.objects.create(
        user=user,
        status=status,
        recipient_name="Ada Lovelace",
        address="Calle Principal 42",
        city="Madrid",
        postal_code="28001",
        country="España",
        total=subtotal,
    )
    OrderItem.objects.create(
        order=order,
        product=product,
        product_name=product.name,
        unit_price=product.price,
        quantity=quantity,
        subtotal=subtotal,
    )
    return order


@pytest.mark.django_db
def test_create_order_from_cart(authenticated_client, user, product_factory):
    product = product_factory(name="Keyboard", price=Decimal("25.50"), stock=5)
    add_cart_item(user, product, quantity=2)

    response = checkout(authenticated_client)

    assert response.status_code == 201
    assert response.data["estado"] == "pendiente"
    assert response.data["nombre_destinatario"] == "Ada Lovelace"
    assert response.data["total"] == "51.00"
    assert response.data["articulos"] == [
        {
            "id": response.data["articulos"][0]["id"],
            "producto": product.id,
            "nombre_producto": "Keyboard",
            "precio_unitario": "25.50",
            "cantidad": 2,
            "subtotal": "51.00",
        }
    ]
    assert Order.objects.filter(user=user).count() == 1


@pytest.mark.django_db
def test_checkout_rejects_empty_cart(authenticated_client):
    response = checkout(authenticated_client)

    assert response.status_code == 400
    assert_error_response(response, "regla_de_negocio", "carrito")
    assert not Order.objects.exists()


@pytest.mark.django_db
def test_checkout_rejects_insufficient_stock(
    authenticated_client,
    user,
    product_factory,
):
    product = product_factory(stock=2)
    item = add_cart_item(user, product, quantity=3)

    response = checkout(authenticated_client)

    product.refresh_from_db()
    assert response.status_code == 400
    assert_error_response(response, "regla_de_negocio", "carrito")
    assert product.stock == 2
    assert CartItem.objects.filter(pk=item.pk).exists()
    assert not Order.objects.exists()


@pytest.mark.django_db
def test_checkout_reduces_stock(authenticated_client, user, product_factory):
    product = product_factory(stock=7)
    add_cart_item(user, product, quantity=3)

    response = checkout(authenticated_client)

    product.refresh_from_db()
    assert response.status_code == 201
    assert product.stock == 4


@pytest.mark.django_db
def test_checkout_clears_cart(authenticated_client, user, product_factory):
    item = add_cart_item(user, product_factory(), quantity=2)

    response = checkout(authenticated_client)

    assert response.status_code == 201
    assert not CartItem.objects.filter(pk=item.pk).exists()
    assert Cart.objects.filter(user=user, active=True).exists()


@pytest.mark.django_db
def test_order_keeps_historical_product_data(
    authenticated_client,
    user,
    product_factory,
):
    product = product_factory(name="Original name", price=Decimal("19.99"))
    add_cart_item(user, product)
    checkout_response = checkout(authenticated_client)
    order_id = checkout_response.data["id"]

    product.name = "Changed name"
    product.price = Decimal("99.99")
    product.save(update_fields=("name", "price", "updated_at"))
    response = authenticated_client.get(reverse("order-detail", args=[order_id]))

    item = response.data["articulos"][0]
    assert response.status_code == 200
    assert item["nombre_producto"] == "Original name"
    assert item["precio_unitario"] == "19.99"
    assert item["subtotal"] == "19.99"
    assert response.data["total"] == "19.99"


@pytest.mark.django_db
def test_order_list_only_returns_own_orders(
    authenticated_client,
    user,
    user_factory,
    product_factory,
):
    own_order = create_order_record(user, product_factory())
    other_user = user_factory()
    create_order_record(other_user, product_factory())

    response = authenticated_client.get(reverse("order-list-create"))

    assert response.status_code == 200
    assert [order["id"] for order in response.data] == [own_order.id]


@pytest.mark.django_db
def test_user_cannot_access_another_users_order(
    authenticated_client,
    user_factory,
    product_factory,
):
    other_user = user_factory()
    order = create_order_record(other_user, product_factory())

    detail_response = authenticated_client.get(reverse("order-detail", args=[order.id]))
    cancel_response = authenticated_client.post(
        reverse("order-cancel", args=[order.id])
    )

    assert detail_response.status_code == 404
    assert cancel_response.status_code == 404
    assert_error_response(detail_response, "recurso_no_encontrado")
    assert_error_response(cancel_response, "recurso_no_encontrado")


@pytest.mark.django_db
def test_order_detail(authenticated_client, user, product_factory):
    order = create_order_record(user, product_factory(name="Mouse"))

    response = authenticated_client.get(reverse("order-detail", args=[order.id]))

    assert response.status_code == 200
    assert response.data["id"] == order.id
    assert response.data["estado"] == "confirmado"
    assert response.data["articulos"][0]["nombre_producto"] == "Mouse"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "initial_status",
    (Order.Status.PENDING, Order.Status.CONFIRMED),
)
def test_cancel_allowed_order_statuses(
    initial_status,
    authenticated_client,
    user,
    product_factory,
):
    order = create_order_record(
        user,
        product_factory(),
        status=initial_status,
    )

    response = authenticated_client.post(reverse("order-cancel", args=[order.id]))

    order.refresh_from_db()
    assert response.status_code == 200
    assert response.data["estado"] == "cancelado"
    assert order.status == Order.Status.CANCELED


@pytest.mark.django_db
def test_cancel_returns_stock(authenticated_client, user, product_factory):
    product = product_factory(stock=5)
    add_cart_item(user, product, quantity=2)
    order_id = checkout(authenticated_client).data["id"]
    product.refresh_from_db()
    assert product.stock == 3

    response = authenticated_client.post(reverse("order-cancel", args=[order_id]))

    product.refresh_from_db()
    assert response.status_code == 200
    assert product.stock == 5


@pytest.mark.django_db
@pytest.mark.parametrize(
    "initial_status",
    (Order.Status.SHIPPED, Order.Status.DELIVERED, Order.Status.CANCELED),
)
def test_cancel_rejects_forbidden_statuses(
    initial_status,
    authenticated_client,
    user,
    product_factory,
):
    product = product_factory(stock=5)
    order = create_order_record(user, product, status=initial_status)

    response = authenticated_client.post(reverse("order-cancel", args=[order.id]))

    product.refresh_from_db()
    assert response.status_code == 400
    assert_error_response(response, "regla_de_negocio", "estado")
    assert product.stock == 5


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("method", "url_name", "args"),
    (
        ("get", "order-list-create", None),
        ("post", "order-list-create", None),
        ("get", "order-detail", (1,)),
        ("post", "order-cancel", (1,)),
    ),
)
def test_order_endpoints_require_authentication(
    method,
    url_name,
    args,
    api_client,
):
    response = getattr(api_client, method)(
        reverse(url_name, args=args),
        {},
        format="json",
    )

    assert response.status_code == 401
    assert_error_response(response, "autenticacion_requerida")


@pytest.mark.django_db
def test_checkout_prevents_overselling(user_factory, product_factory):
    first_user = user_factory(username="first-buyer")
    second_user = user_factory(username="second-buyer")
    product = product_factory(stock=3)
    add_cart_item(first_user, product, quantity=2)
    add_cart_item(second_user, product, quantity=2)
    first_client = authenticate_client(APIClient(), first_user)
    second_client = authenticate_client(APIClient(), second_user)

    first_response = checkout(first_client)
    second_response = checkout(second_client)

    product.refresh_from_db()
    assert first_response.status_code == 201
    assert second_response.status_code == 400
    assert product.stock == 1
    assert Order.objects.count() == 1
