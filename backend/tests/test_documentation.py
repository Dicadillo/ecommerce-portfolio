import json

import pytest
from django.test import Client
from django.urls import reverse


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def schema_response(client):
    return client.get(reverse("api-schema"), HTTP_ACCEPT="application/json")


def test_openapi_schema_returns_success(schema_response):
    assert schema_response.status_code == 200
    assert schema_response.headers["Content-Type"].startswith("application/json")


def test_swagger_ui_returns_success(client):
    response = client.get(reverse("swagger-ui"))

    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith("text/html")


def test_redoc_returns_success(client):
    response = client.get(reverse("redoc"))

    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith("text/html")


def test_schema_includes_main_endpoints_and_jwt_security(schema_response):
    schema = json.loads(schema_response.content)
    expected_paths = {
        "/api/categorias/",
        "/api/categorias/{id}/",
        "/api/productos/",
        "/api/productos/{id}/",
        "/api/autenticacion/registro/",
        "/api/autenticacion/login/",
        "/api/autenticacion/refrescar/",
        "/api/autenticacion/perfil/",
        "/api/carrito/",
        "/api/carrito/articulos/",
        "/api/carrito/articulos/{item_id}/",
        "/api/carrito/vaciar/",
        "/api/pedidos/",
        "/api/pedidos/{order_id}/",
        "/api/pedidos/{order_id}/cancelar/",
        "/api/pagos/",
        "/api/pagos/{payment_id}/",
        "/api/pagos/{payment_id}/reembolsar/",
    }

    assert expected_paths <= set(schema["paths"])

    security_schemes = schema["components"]["securitySchemes"]
    assert any(
        scheme.get("type") == "http" and scheme.get("scheme") == "bearer"
        for scheme in security_schemes.values()
    )
    assert schema["paths"]["/api/carrito/"]["get"]["security"] == [{"jwtAuth": []}]
    assert "security" not in schema["paths"]["/api/autenticacion/registro/"]["post"]

    error_schema = schema["components"]["schemas"]["Error"]
    assert "error" in error_schema["properties"]
    assert "400" in schema["paths"]["/api/carrito/articulos/"]["post"]["responses"]
    assert "401" in schema["paths"]["/api/carrito/articulos/"]["post"]["responses"]
