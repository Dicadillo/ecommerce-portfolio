from decimal import Decimal
from typing import Any

import pytest

from clients.api_client import EcommerceApiClient
from helpers.assertions import assert_error, assert_status
from helpers.workflows import add_product_to_cart


@pytest.mark.smoke
def test_returns_clean_cart(
    api_client: EcommerceApiClient,
    auth_headers: dict[str, str],
    clean_cart: dict[str, Any],
) -> None:
    response = api_client.get("carrito/", headers=auth_headers)

    assert_status(response, 200)
    assert response.json() == clean_cart
    assert clean_cart["cantidad_total"] == 0
    assert Decimal(clean_cart["total"]) == Decimal("0.00")


@pytest.mark.smoke
def test_adds_available_product_to_cart(
    api_client: EcommerceApiClient,
    auth_headers: dict[str, str],
    clean_cart: dict[str, Any],
    available_product: dict[str, Any],
) -> None:
    del clean_cart
    item = add_product_to_cart(
        api_client,
        auth_headers,
        product_id=available_product["id"],
    )
    cart_response = api_client.get("carrito/", headers=auth_headers)

    assert_status(cart_response, 200)
    cart = cart_response.json()
    assert item["producto"] == available_product["id"]
    assert item["cantidad"] == 1
    assert Decimal(item["subtotal"]) == Decimal(available_product["precio"])
    assert cart["cantidad_total"] == 1
    assert cart["articulos"] == [item]


@pytest.mark.regression
def test_updates_and_deletes_cart_item(
    api_client: EcommerceApiClient,
    auth_headers: dict[str, str],
    clean_cart: dict[str, Any],
    available_product: dict[str, Any],
) -> None:
    del clean_cart
    item = add_product_to_cart(
        api_client,
        auth_headers,
        product_id=available_product["id"],
    )

    update_response = api_client.patch(
        f"carrito/articulos/{item['id']}/",
        headers=auth_headers,
        json={"cantidad": 2},
    )
    assert_status(update_response, 200)
    assert update_response.json()["cantidad"] == 2

    delete_response = api_client.delete(
        f"carrito/articulos/{item['id']}/",
        headers=auth_headers,
    )
    assert_status(delete_response, 204)
    cart_response = api_client.get("carrito/", headers=auth_headers)
    assert_status(cart_response, 200)
    assert cart_response.json()["articulos"] == []


@pytest.mark.regression
def test_cart_requires_authentication(api_client: EcommerceApiClient) -> None:
    response = api_client.get("carrito/")

    assert_error(response, 401, code="autenticacion_requerida")


@pytest.mark.regression
@pytest.mark.parametrize("quantity", [0, -1])
def test_rejects_invalid_cart_quantity(
    api_client: EcommerceApiClient,
    auth_headers: dict[str, str],
    clean_cart: dict[str, Any],
    available_product: dict[str, Any],
    quantity: int,
) -> None:
    del clean_cart
    response = api_client.post(
        "carrito/articulos/",
        headers=auth_headers,
        json={"producto": available_product["id"], "cantidad": quantity},
    )

    assert_error(
        response,
        400,
        code="validacion_incorrecta",
        detail="cantidad",
    )


@pytest.mark.regression
def test_rejects_quantity_above_stock(
    api_client: EcommerceApiClient,
    auth_headers: dict[str, str],
    clean_cart: dict[str, Any],
    available_product: dict[str, Any],
) -> None:
    del clean_cart
    response = api_client.post(
        "carrito/articulos/",
        headers=auth_headers,
        json={
            "producto": available_product["id"],
            "cantidad": available_product["stock"] + 1,
        },
    )

    assert_error(response, 400, code="regla_de_negocio", detail="cantidad")


@pytest.mark.regression
def test_rejects_unknown_product(
    api_client: EcommerceApiClient,
    auth_headers: dict[str, str],
    clean_cart: dict[str, Any],
    nonexistent_product_id: int,
) -> None:
    del clean_cart
    response = api_client.post(
        "carrito/articulos/",
        headers=auth_headers,
        json={"producto": nonexistent_product_id, "cantidad": 1},
    )

    assert_error(
        response,
        400,
        code="validacion_incorrecta",
        detail="producto",
    )
