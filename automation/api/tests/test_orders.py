from collections.abc import Callable
from typing import Any

import pytest

from clients.api_client import EcommerceApiClient
from factories.data_factory import build_delivery_data
from helpers.assertions import assert_error, assert_status
from helpers.workflows import add_product_to_cart


@pytest.mark.smoke
def test_creates_order_from_cart_and_preserves_item_snapshot(
    pending_order: dict[str, Any],
    available_product: dict[str, Any],
) -> None:
    assert pending_order["estado"] == "pendiente"
    assert pending_order["articulos"][0]["producto"] == available_product["id"]
    assert (
        pending_order["articulos"][0]["nombre_producto"] == available_product["nombre"]
    )
    assert (
        pending_order["articulos"][0]["precio_unitario"] == available_product["precio"]
    )
    assert pending_order["total"] == available_product["precio"]


@pytest.mark.regression
def test_lists_and_retrieves_own_order(
    api_client: EcommerceApiClient,
    auth_headers: dict[str, str],
    pending_order: dict[str, Any],
) -> None:
    list_response = api_client.get("pedidos/", headers=auth_headers)
    detail_response = api_client.get(
        f"pedidos/{pending_order['id']}/",
        headers=auth_headers,
    )

    assert_status(list_response, 200)
    assert pending_order["id"] in [order["id"] for order in list_response.json()]
    assert_status(detail_response, 200)
    assert detail_response.json() == pending_order


@pytest.mark.regression
def test_rejects_checkout_with_empty_cart(
    api_client: EcommerceApiClient,
    auth_headers: dict[str, str],
    clean_cart: dict[str, Any],
) -> None:
    del clean_cart
    response = api_client.post(
        "pedidos/",
        headers=auth_headers,
        json=build_delivery_data(),
    )

    assert_error(response, 400, code="regla_de_negocio", detail="carrito")


@pytest.mark.smoke
def test_cancels_pending_order(
    api_client: EcommerceApiClient,
    auth_headers: dict[str, str],
    pending_order: dict[str, Any],
) -> None:
    response = api_client.post(
        f"pedidos/{pending_order['id']}/cancelar/",
        headers=auth_headers,
    )

    assert_status(response, 200)
    assert response.json()["estado"] == "cancelado"


@pytest.mark.regression
def test_cannot_access_another_users_order(
    api_client: EcommerceApiClient,
    auth_session: dict[str, Any],
    user_session_factory: Callable[[], dict[str, Any]],
    order_factory: Callable[[dict[str, Any], dict[str, Any], int], dict[str, Any]],
    available_product: dict[str, Any],
) -> None:
    order = order_factory(auth_session, available_product, 1)
    other_session = user_session_factory()

    response = api_client.get(
        f"pedidos/{order['id']}/",
        headers=other_session["headers"],
    )

    assert_error(response, 404, code="recurso_no_encontrado")


@pytest.mark.regression
def test_rejects_order_with_missing_delivery_data(
    api_client: EcommerceApiClient,
    auth_headers: dict[str, str],
    clean_cart: dict[str, Any],
    available_product: dict[str, Any],
) -> None:
    del clean_cart
    add_product_to_cart(
        api_client,
        auth_headers,
        product_id=available_product["id"],
    )

    response = api_client.post("pedidos/", headers=auth_headers, json={})

    error = assert_error(
        response,
        400,
        code="validacion_incorrecta",
        detail="nombre_destinatario",
    )
    assert {"direccion", "ciudad", "codigo_postal", "pais"} <= set(error["detalles"])


@pytest.mark.regression
def test_orders_require_authentication(api_client: EcommerceApiClient) -> None:
    response = api_client.get("pedidos/")

    assert_error(response, 401, code="autenticacion_requerida")
