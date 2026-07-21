from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from orders.models import Order, OrderItem
from payments.models import Payment
from tests.payments.conftest import authenticate_client

APPROVED_CARD = "4111111111111111"
REJECTED_CARD = "4000000000000002"
PENDING_CARD = "5555555555554444"


def create_order(user, product, status=Order.Status.PENDING, quantity=2):
    subtotal = product.price * quantity
    order = Order.objects.create(
        user=user,
        status=status,
        recipient_name="Santi García",
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


def payment_payload(order_id, card_number=APPROVED_CARD):
    return {
        "pedido": order_id,
        "numero_tarjeta": card_number,
        "titular": "Santi García",
        "fecha_expiracion": "12/30",
        "cvv": "123",
    }


def pay(client, order, card_number=APPROVED_CARD):
    return client.post(
        reverse("payment-create"),
        payment_payload(order.id, card_number),
        format="json",
    )


@pytest.mark.django_db
def test_approved_payment(authenticated_client, user, product_factory):
    order = create_order(user, product_factory(price=Decimal("12.50")))

    response = pay(authenticated_client, order)

    order.refresh_from_db()
    assert response.status_code == 201
    assert response.data["estado"] == "aprobado"
    assert response.data["pedido"] == order.id
    assert response.data["ultimos_cuatro"] == "1111"
    assert order.status == Order.Status.CONFIRMED


@pytest.mark.django_db
def test_rejected_payment(authenticated_client, user, product_factory):
    order = create_order(user, product_factory())

    response = pay(authenticated_client, order, REJECTED_CARD)

    order.refresh_from_db()
    assert response.status_code == 201
    assert response.data["estado"] == "rechazado"
    assert order.status == Order.Status.PENDING


@pytest.mark.django_db
def test_pending_payment(authenticated_client, user, product_factory):
    order = create_order(user, product_factory())

    response = pay(authenticated_client, order, PENDING_CARD)

    order.refresh_from_db()
    assert response.status_code == 201
    assert response.data["estado"] == "pendiente"
    assert order.status == Order.Status.PENDING


@pytest.mark.django_db
def test_nonexistent_order(authenticated_client):
    response = authenticated_client.post(
        reverse("payment-create"),
        payment_payload(999999),
        format="json",
    )

    assert response.status_code == 404
    assert "pedido" in response.data


@pytest.mark.django_db
def test_cannot_pay_another_users_order(
    authenticated_client,
    user_factory,
    product_factory,
):
    other_user = user_factory()
    order = create_order(other_user, product_factory())

    response = pay(authenticated_client, order)

    assert response.status_code == 404
    assert not Payment.objects.exists()


@pytest.mark.django_db
def test_canceled_order_cannot_be_paid(authenticated_client, user, product_factory):
    order = create_order(
        user,
        product_factory(),
        status=Order.Status.CANCELED,
    )

    response = pay(authenticated_client, order)

    assert response.status_code == 400
    assert "pedido" in response.data
    assert not Payment.objects.exists()


@pytest.mark.django_db
def test_order_cannot_have_duplicate_payment(
    authenticated_client,
    user,
    product_factory,
):
    order = create_order(user, product_factory())
    first_response = pay(authenticated_client, order)

    second_response = pay(authenticated_client, order)

    assert first_response.status_code == 201
    assert second_response.status_code == 400
    assert Payment.objects.filter(order=order).count() == 1


@pytest.mark.django_db
def test_payment_amount_matches_order_total(
    authenticated_client,
    user,
    product_factory,
):
    order = create_order(
        user,
        product_factory(price=Decimal("17.25")),
        quantity=3,
    )

    response = pay(authenticated_client, order)

    payment = Payment.objects.get(order=order)
    assert response.status_code == 201
    assert response.data["importe"] == "51.75"
    assert payment.amount == order.total == Decimal("51.75")


@pytest.mark.django_db
def test_payment_detail(authenticated_client, user, product_factory):
    order = create_order(user, product_factory())
    payment_id = pay(authenticated_client, order).data["id"]

    response = authenticated_client.get(reverse("payment-detail", args=[payment_id]))

    assert response.status_code == 200
    assert response.data["id"] == payment_id
    assert response.data["pedido"] == order.id
    assert response.data["estado"] == "aprobado"


@pytest.mark.django_db
def test_cannot_access_another_users_payment(
    authenticated_client,
    user_factory,
    product_factory,
):
    other_user = user_factory()
    other_client = authenticate_client(APIClient(), other_user)
    order = create_order(other_user, product_factory())
    payment_id = pay(other_client, order).data["id"]

    response = authenticated_client.get(reverse("payment-detail", args=[payment_id]))

    assert response.status_code == 404


@pytest.mark.django_db
def test_full_card_number_and_cvv_are_never_stored(
    authenticated_client,
    user,
    product_factory,
):
    order = create_order(user, product_factory())

    response = pay(authenticated_client, order)

    payment = Payment.objects.get(order=order)
    field_names = {field.name for field in Payment._meta.fields}
    stored_values = {str(value) for value in payment.__dict__.values()}
    assert response.status_code == 201
    assert payment.card_last_four == "1111"
    assert "card_number" not in field_names
    assert "cvv" not in field_names
    assert APPROVED_CARD not in stored_values
    assert "123" not in stored_values


@pytest.mark.django_db
def test_successful_refund(authenticated_client, user, product_factory):
    order = create_order(user, product_factory())
    payment_id = pay(authenticated_client, order).data["id"]

    response = authenticated_client.post(reverse("payment-refund", args=[payment_id]))

    order.refresh_from_db()
    assert response.status_code == 200
    assert response.data["estado"] == "reembolsado"
    assert order.status == Order.Status.CANCELED


@pytest.mark.django_db
def test_refund_returns_stock(authenticated_client, user, product_factory):
    product = product_factory(stock=3)
    order = create_order(user, product, quantity=2)
    payment_id = pay(authenticated_client, order).data["id"]

    response = authenticated_client.post(reverse("payment-refund", args=[payment_id]))

    product.refresh_from_db()
    assert response.status_code == 200
    assert product.stock == 5


@pytest.mark.django_db
@pytest.mark.parametrize("card_number", (REJECTED_CARD, PENDING_CARD))
def test_non_approved_payment_cannot_be_refunded(
    card_number,
    authenticated_client,
    user,
    product_factory,
):
    order = create_order(user, product_factory())
    payment_id = pay(authenticated_client, order, card_number).data["id"]

    response = authenticated_client.post(reverse("payment-refund", args=[payment_id]))

    assert response.status_code == 400
    assert "estado" in response.data


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("method", "url_name", "args"),
    (
        ("post", "payment-create", None),
        ("get", "payment-detail", (1,)),
        ("post", "payment-refund", (1,)),
    ),
)
def test_payment_endpoints_require_authentication(
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
    assert "detalle" in response.data


@pytest.mark.django_db
def test_invalid_card_number_is_rejected(
    authenticated_client,
    user,
    product_factory,
):
    order = create_order(user, product_factory())

    response = pay(authenticated_client, order, "4111111111111112")

    assert response.status_code == 400
    assert "numero_tarjeta" in response.data
    assert not Payment.objects.exists()
