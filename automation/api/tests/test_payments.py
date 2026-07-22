from typing import Any

import pytest

from clients.api_client import EcommerceApiClient
from helpers.assertions import assert_error, assert_status

APPROVED_CARD = "4111111111111111"
REJECTED_CARD = "4000000000000002"
PENDING_CARD = "5555555555554444"


def payment_payload(order_id: int, card_number: str) -> dict[str, Any]:
    return {
        "pedido": order_id,
        "numero_tarjeta": card_number,
        "titular": "Cliente Automatización",
        "fecha_expiracion": "12/30",
        "cvv": "123",
    }


@pytest.mark.smoke
def test_approves_simulated_payment_and_returns_safe_detail(
    api_client: EcommerceApiClient,
    auth_headers: dict[str, str],
    pending_order: dict[str, Any],
) -> None:
    response = api_client.post(
        "pagos/",
        headers=auth_headers,
        json=payment_payload(pending_order["id"], APPROVED_CARD),
    )

    assert_status(response, 201)
    payment = response.json()
    assert payment["estado"] == "aprobado"
    assert payment["pedido"] == pending_order["id"]
    assert payment["importe"] == pending_order["total"]
    assert payment["ultimos_cuatro"] == "1111"
    assert "numero_tarjeta" not in payment
    assert "cvv" not in payment

    detail_response = api_client.get(
        f"pagos/{payment['id']}/",
        headers=auth_headers,
    )
    assert_status(detail_response, 200)
    assert detail_response.json() == payment

    order_response = api_client.get(
        f"pedidos/{pending_order['id']}/",
        headers=auth_headers,
    )
    assert_status(order_response, 200)
    assert order_response.json()["estado"] == "confirmado"


@pytest.mark.regression
def test_rejects_simulated_payment(
    api_client: EcommerceApiClient,
    auth_headers: dict[str, str],
    pending_order: dict[str, Any],
) -> None:
    response = api_client.post(
        "pagos/",
        headers=auth_headers,
        json=payment_payload(pending_order["id"], REJECTED_CARD),
    )

    assert_status(response, 201)
    assert response.json()["estado"] == "rechazado"
    assert response.json()["ultimos_cuatro"] == "0002"


@pytest.mark.regression
def test_leaves_other_valid_card_payment_pending(
    api_client: EcommerceApiClient,
    auth_headers: dict[str, str],
    pending_order: dict[str, Any],
) -> None:
    response = api_client.post(
        "pagos/",
        headers=auth_headers,
        json=payment_payload(pending_order["id"], PENDING_CARD),
    )

    assert_status(response, 201)
    assert response.json()["estado"] == "pendiente"


@pytest.mark.regression
def test_rejects_duplicate_payment_for_order(
    api_client: EcommerceApiClient,
    auth_headers: dict[str, str],
    pending_order: dict[str, Any],
) -> None:
    first_response = api_client.post(
        "pagos/",
        headers=auth_headers,
        json=payment_payload(pending_order["id"], APPROVED_CARD),
    )
    assert_status(first_response, 201)

    duplicate_response = api_client.post(
        "pagos/",
        headers=auth_headers,
        json=payment_payload(pending_order["id"], APPROVED_CARD),
    )

    assert_error(
        duplicate_response,
        400,
        code="regla_de_negocio",
        detail="pedido",
    )


@pytest.mark.smoke
def test_refunds_approved_payment_and_cancels_order(
    api_client: EcommerceApiClient,
    auth_headers: dict[str, str],
    pending_order: dict[str, Any],
) -> None:
    payment_response = api_client.post(
        "pagos/",
        headers=auth_headers,
        json=payment_payload(pending_order["id"], APPROVED_CARD),
    )
    assert_status(payment_response, 201)
    payment = payment_response.json()

    refund_response = api_client.post(
        f"pagos/{payment['id']}/reembolsar/",
        headers=auth_headers,
    )

    assert_status(refund_response, 200)
    assert refund_response.json()["estado"] == "reembolsado"
    order_response = api_client.get(
        f"pedidos/{pending_order['id']}/",
        headers=auth_headers,
    )
    assert_status(order_response, 200)
    assert order_response.json()["estado"] == "cancelado"


@pytest.mark.regression
def test_rejects_refund_for_non_approved_payment(
    api_client: EcommerceApiClient,
    auth_headers: dict[str, str],
    pending_order: dict[str, Any],
) -> None:
    payment_response = api_client.post(
        "pagos/",
        headers=auth_headers,
        json=payment_payload(pending_order["id"], REJECTED_CARD),
    )
    assert_status(payment_response, 201)

    refund_response = api_client.post(
        f"pagos/{payment_response.json()['id']}/reembolsar/",
        headers=auth_headers,
    )

    assert_error(
        refund_response,
        400,
        code="regla_de_negocio",
        detail="estado",
    )


@pytest.mark.regression
def test_rejects_payment_for_canceled_order(
    api_client: EcommerceApiClient,
    auth_headers: dict[str, str],
    pending_order: dict[str, Any],
) -> None:
    cancel_response = api_client.post(
        f"pedidos/{pending_order['id']}/cancelar/",
        headers=auth_headers,
    )
    assert_status(cancel_response, 200)

    payment_response = api_client.post(
        "pagos/",
        headers=auth_headers,
        json=payment_payload(pending_order["id"], APPROVED_CARD),
    )

    assert_error(
        payment_response,
        400,
        code="regla_de_negocio",
        detail="pedido",
    )


@pytest.mark.regression
def test_payment_requires_authentication(
    api_client: EcommerceApiClient,
    pending_order: dict[str, Any],
) -> None:
    response = api_client.post(
        "pagos/",
        json=payment_payload(pending_order["id"], APPROVED_CARD),
    )

    assert_error(response, 401, code="autenticacion_requerida")
