import pytest
from django.test import Client


@pytest.mark.parametrize(
    "origin",
    (
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ),
)
def test_cors_allows_local_frontend_origins(origin):
    response = Client().get("/api/salud/", HTTP_ORIGIN=origin)

    assert response.status_code == 200
    assert response.headers["Access-Control-Allow-Origin"] == origin


def test_cors_does_not_allow_an_unknown_origin():
    response = Client().get(
        "/api/salud/",
        HTTP_ORIGIN="https://frontend-no-permitido.example",
    )

    assert response.status_code == 200
    assert "Access-Control-Allow-Origin" not in response.headers


def test_cors_answers_a_local_preflight_request():
    response = Client().options(
        "/api/autenticacion/login/",
        HTTP_ORIGIN="http://localhost:5173",
        HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
        HTTP_ACCESS_CONTROL_REQUEST_HEADERS="authorization,content-type",
    )

    assert response.status_code == 200
    assert response.headers["Access-Control-Allow-Origin"] == "http://localhost:5173"
    assert "POST" in response.headers["Access-Control-Allow-Methods"]
    allowed_headers = response.headers["Access-Control-Allow-Headers"].lower()
    assert "authorization" in allowed_headers
    assert "content-type" in allowed_headers
