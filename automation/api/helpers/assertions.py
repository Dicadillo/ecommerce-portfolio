from typing import Any

import httpx

SENSITIVE_FIELDS = {
    "acceso",
    "authorization",
    "confirmacion_contrasena",
    "contrasena",
    "cvv",
    "numero_tarjeta",
    "refresco",
}


def _redact(value: Any, key: str | None = None) -> Any:
    if key and key.lower() in SENSITIVE_FIELDS:
        return "<omitido>"
    if isinstance(value, dict):
        return {item_key: _redact(item, item_key) for item_key, item in value.items()}
    if isinstance(value, list):
        return [_redact(item) for item in value]
    return value


def safe_response_body(response: httpx.Response) -> Any:
    try:
        return _redact(response.json())
    except ValueError:
        return "<respuesta no JSON>"


def assert_status(response: httpx.Response, expected_status: int) -> None:
    assert response.status_code == expected_status, (
        f"Se esperaba HTTP {expected_status} y se recibió {response.status_code}. "
        f"Respuesta segura: {safe_response_body(response)!r}"
    )


def assert_error(
    response: httpx.Response,
    expected_status: int,
    *,
    code: str | None = None,
    detail: str | None = None,
) -> dict[str, Any]:
    assert_status(response, expected_status)
    body = response.json()
    assert set(body) == {"error"}
    error = body["error"]
    assert {"codigo", "mensaje", "detalles"} <= set(error)
    if code is not None:
        assert error["codigo"] == code
    if detail is not None:
        assert detail in error["detalles"]
    return error
