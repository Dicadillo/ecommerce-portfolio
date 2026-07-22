import os
from collections.abc import Callable, Iterator
from typing import Any

import pytest

from clients.api_client import EcommerceApiClient
from factories.data_factory import build_complete_user_data, build_delivery_data
from helpers.assertions import assert_status
from helpers.config import ApiSettings, load_settings
from helpers.workflows import (
    add_product_to_cart,
    cancel_order_if_possible,
    create_order,
    register_and_login,
)


def pytest_xdist_auto_num_workers(config: pytest.Config) -> int:
    """Mantiene el paralelismo útil sin saturar el backend local compartido."""
    del config
    return min(os.cpu_count() or 1, 4)


@pytest.fixture(scope="session")
def api_settings() -> ApiSettings:
    return load_settings()


@pytest.fixture(scope="session")
def api_client(api_settings: ApiSettings) -> Iterator[EcommerceApiClient]:
    client = EcommerceApiClient(
        base_url=api_settings.base_url,
        timeout=api_settings.timeout_seconds,
    )
    yield client
    client.close()


@pytest.fixture
def new_user_data() -> dict[str, str]:
    return build_complete_user_data()


@pytest.fixture
def registered_user(
    api_client: EcommerceApiClient,
    new_user_data: dict[str, str],
) -> dict[str, Any]:
    response = api_client.post("autenticacion/registro/", json=new_user_data)
    assert_status(response, 201)
    return {"credentials": new_user_data, "profile": response.json()}


@pytest.fixture
def login_tokens(
    api_client: EcommerceApiClient,
    registered_user: dict[str, Any],
) -> dict[str, str]:
    credentials = registered_user["credentials"]
    response = api_client.post(
        "autenticacion/login/",
        json={
            "usuario": credentials["usuario"],
            "contrasena": credentials["contrasena"],
        },
    )
    assert_status(response, 200)
    return response.json()


@pytest.fixture
def access_token(login_tokens: dict[str, str]) -> str:
    return login_tokens["acceso"]


@pytest.fixture
def auth_headers(access_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def auth_session(
    registered_user: dict[str, Any],
    login_tokens: dict[str, str],
    auth_headers: dict[str, str],
) -> dict[str, Any]:
    return {
        **registered_user,
        "access": login_tokens["acceso"],
        "refresh": login_tokens["refresco"],
        "headers": auth_headers,
    }


@pytest.fixture
def user_session_factory(
    api_client: EcommerceApiClient,
) -> Callable[[], dict[str, Any]]:
    def create_user_session() -> dict[str, Any]:
        return register_and_login(api_client, build_complete_user_data())

    return create_user_session


@pytest.fixture(scope="session")
def available_product(api_client: EcommerceApiClient) -> dict[str, Any]:
    response = api_client.get(
        "productos/",
        params={"activo": "true", "con_stock": "true"},
    )
    assert_status(response, 200)
    products = response.json()["resultados"]
    if not products:
        pytest.fail(
            "No hay productos demo activos con stock. Ejecuta cargar_datos_demo."
        )
    return max(products, key=lambda product: product["stock"])


@pytest.fixture(scope="session")
def nonexistent_product_id(api_client: EcommerceApiClient) -> int:
    response = api_client.get("productos/")
    assert_status(response, 200)
    product_ids = [product["id"] for product in response.json()["resultados"]]
    return max(product_ids, default=0) + 10_000_000


@pytest.fixture
def clean_cart(
    api_client: EcommerceApiClient,
    auth_headers: dict[str, str],
) -> Iterator[dict[str, Any]]:
    clear_response = api_client.delete("carrito/vaciar/", headers=auth_headers)
    assert_status(clear_response, 204)
    cart_response = api_client.get("carrito/", headers=auth_headers)
    assert_status(cart_response, 200)
    cart = cart_response.json()
    assert cart["articulos"] == []
    yield cart
    api_client.delete("carrito/vaciar/", headers=auth_headers)


@pytest.fixture
def order_factory(
    api_client: EcommerceApiClient,
) -> Iterator[Callable[[dict[str, Any], dict[str, Any], int], dict[str, Any]]]:
    created_orders: list[tuple[dict[str, str], int]] = []

    def create_pending_order(
        session: dict[str, Any],
        product: dict[str, Any],
        quantity: int = 1,
    ) -> dict[str, Any]:
        headers = session["headers"]
        api_client.delete("carrito/vaciar/", headers=headers)
        add_product_to_cart(
            api_client,
            headers,
            product_id=product["id"],
            quantity=quantity,
        )
        order = create_order(api_client, headers, build_delivery_data())
        created_orders.append((headers, order["id"]))
        return order

    yield create_pending_order

    for headers, order_id in reversed(created_orders):
        cancel_order_if_possible(api_client, headers, order_id)


@pytest.fixture
def pending_order(
    order_factory: Callable[[dict[str, Any], dict[str, Any], int], dict[str, Any]],
    auth_session: dict[str, Any],
    available_product: dict[str, Any],
) -> dict[str, Any]:
    return order_factory(auth_session, available_product, 1)
