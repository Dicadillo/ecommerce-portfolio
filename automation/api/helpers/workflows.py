from typing import Any

from clients.api_client import EcommerceApiClient
from helpers.assertions import assert_status


def register_and_login(
    api_client: EcommerceApiClient,
    user_data: dict[str, str],
) -> dict[str, Any]:
    register_response = api_client.post("autenticacion/registro/", json=user_data)
    assert_status(register_response, 201)

    login_response = api_client.post(
        "autenticacion/login/",
        json={
            "usuario": user_data["usuario"],
            "contrasena": user_data["contrasena"],
        },
    )
    assert_status(login_response, 200)
    tokens = login_response.json()
    return {
        "credentials": user_data,
        "profile": register_response.json(),
        "access": tokens["acceso"],
        "refresh": tokens["refresco"],
        "headers": {"Authorization": f"Bearer {tokens['acceso']}"},
    }


def add_product_to_cart(
    api_client: EcommerceApiClient,
    headers: dict[str, str],
    product_id: int,
    quantity: int = 1,
) -> dict[str, Any]:
    response = api_client.post(
        "carrito/articulos/",
        headers=headers,
        json={"producto": product_id, "cantidad": quantity},
    )
    assert response.status_code in {200, 201}
    return response.json()


def create_order(
    api_client: EcommerceApiClient,
    headers: dict[str, str],
    delivery_data: dict[str, str],
) -> dict[str, Any]:
    response = api_client.post("pedidos/", headers=headers, json=delivery_data)
    assert_status(response, 201)
    return response.json()


def cancel_order_if_possible(
    api_client: EcommerceApiClient,
    headers: dict[str, str],
    order_id: int,
) -> None:
    detail_response = api_client.get(f"pedidos/{order_id}/", headers=headers)
    if detail_response.status_code != 200:
        return
    if detail_response.json()["estado"] in {"pendiente", "confirmado"}:
        api_client.post(f"pedidos/{order_id}/cancelar/", headers=headers)
