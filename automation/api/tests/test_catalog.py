from typing import Any

import pytest

from clients.api_client import EcommerceApiClient
from helpers.assertions import assert_error, assert_status


@pytest.mark.smoke
def test_lists_categories(api_client: EcommerceApiClient) -> None:
    response = api_client.get("categorias/")

    assert_status(response, 200)
    body = response.json()
    assert body["conteo"] >= 1
    assert body["resultados"]
    assert {"id", "nombre", "slug", "activo"} <= set(body["resultados"][0])


@pytest.mark.smoke
def test_lists_and_retrieves_products(
    api_client: EcommerceApiClient,
    available_product: dict[str, Any],
) -> None:
    list_response = api_client.get("productos/")
    detail_response = api_client.get(f"productos/{available_product['id']}/")

    assert_status(list_response, 200)
    assert list_response.json()["conteo"] >= 1
    assert_status(detail_response, 200)
    assert detail_response.json() == available_product


@pytest.mark.regression
def test_searches_products_by_name(
    api_client: EcommerceApiClient,
    available_product: dict[str, Any],
) -> None:
    search_term = available_product["nombre"].split()[0]
    response = api_client.get("productos/", params={"buscar": search_term})

    assert_status(response, 200)
    products = response.json()["resultados"]
    assert products
    assert all(
        search_term.casefold() in product["nombre"].casefold() for product in products
    )


@pytest.mark.regression
def test_filters_products_by_category(
    api_client: EcommerceApiClient,
    available_product: dict[str, Any],
) -> None:
    response = api_client.get(
        "productos/",
        params={"categoria": available_product["categoria"]},
    )

    assert_status(response, 200)
    products = response.json()["resultados"]
    assert products
    assert all(
        product["categoria"] == available_product["categoria"] for product in products
    )


@pytest.mark.regression
def test_filters_active_products_with_stock(api_client: EcommerceApiClient) -> None:
    response = api_client.get(
        "productos/",
        params={"activo": "true", "con_stock": "true", "tamano_pagina": 100},
    )

    assert_status(response, 200)
    products = response.json()["resultados"]
    assert products
    assert all(
        product["activo"] is True and product["stock"] > 0 for product in products
    )


@pytest.mark.regression
def test_orders_products_by_ascending_price(api_client: EcommerceApiClient) -> None:
    response = api_client.get(
        "productos/",
        params={"ordenar": "precio", "tamano_pagina": 100},
    )

    assert_status(response, 200)
    prices = [float(product["precio"]) for product in response.json()["resultados"]]
    assert prices == sorted(prices)


@pytest.mark.regression
def test_returns_not_found_for_unknown_product(
    api_client: EcommerceApiClient,
    nonexistent_product_id: int,
) -> None:
    response = api_client.get(f"productos/{nonexistent_product_id}/")

    assert_error(response, 404, code="recurso_no_encontrado")
