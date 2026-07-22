from typing import Any

import pytest

from clients.api_client import EcommerceApiClient
from helpers.assertions import assert_error, assert_status


@pytest.mark.smoke
def test_registers_a_unique_user(registered_user: dict[str, Any]) -> None:
    credentials = registered_user["credentials"]
    profile = registered_user["profile"]

    assert profile["usuario"] == credentials["usuario"]
    assert profile["correo"] == credentials["correo"]
    assert "contrasena" not in profile
    assert "confirmacion_contrasena" not in profile


@pytest.mark.smoke
def test_logs_in_with_registered_credentials(login_tokens: dict[str, str]) -> None:
    assert login_tokens["acceso"]
    assert login_tokens["refresco"]
    assert login_tokens["acceso"] != login_tokens["refresco"]


@pytest.mark.smoke
def test_refreshes_access_token(
    api_client: EcommerceApiClient,
    login_tokens: dict[str, str],
) -> None:
    response = api_client.post(
        "autenticacion/refrescar/",
        json={"refresco": login_tokens["refresco"]},
    )

    assert_status(response, 200)
    assert response.json()["acceso"]


@pytest.mark.smoke
def test_returns_authenticated_profile(
    api_client: EcommerceApiClient,
    auth_headers: dict[str, str],
    registered_user: dict[str, Any],
) -> None:
    response = api_client.get("autenticacion/perfil/", headers=auth_headers)

    assert_status(response, 200)
    assert response.json() == registered_user["profile"]


@pytest.mark.regression
def test_rejects_private_access_without_token(api_client: EcommerceApiClient) -> None:
    response = api_client.get("autenticacion/perfil/")

    assert_error(response, 401, code="autenticacion_requerida")


@pytest.mark.regression
def test_rejects_invalid_access_token(api_client: EcommerceApiClient) -> None:
    response = api_client.get(
        "autenticacion/perfil/",
        headers={"Authorization": "Bearer token-invalido"},
    )

    assert_error(response, 401, code="autenticacion_fallida")


@pytest.mark.regression
def test_rejects_missing_registration_fields(api_client: EcommerceApiClient) -> None:
    response = api_client.post("autenticacion/registro/", json={})

    error = assert_error(
        response,
        400,
        code="validacion_incorrecta",
        detail="usuario",
    )
    assert {
        "usuario",
        "correo",
        "contrasena",
        "confirmacion_contrasena",
    } <= set(error["detalles"])


@pytest.mark.regression
def test_rejects_duplicate_username(
    api_client: EcommerceApiClient,
    registered_user: dict[str, Any],
) -> None:
    response = api_client.post(
        "autenticacion/registro/",
        json=registered_user["credentials"],
    )

    assert_error(
        response,
        400,
        code="validacion_incorrecta",
        detail="usuario",
    )


@pytest.mark.regression
def test_rejects_incorrect_login(
    api_client: EcommerceApiClient,
    registered_user: dict[str, Any],
) -> None:
    response = api_client.post(
        "autenticacion/login/",
        json={
            "usuario": registered_user["credentials"]["usuario"],
            "contrasena": "Incorrecta!2026",
        },
    )

    assert_error(response, 401, code="autenticacion_fallida")
