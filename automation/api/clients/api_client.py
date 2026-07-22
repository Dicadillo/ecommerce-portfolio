import logging
from time import perf_counter
from typing import Any

import httpx

logger = logging.getLogger("ecommerce_api.http")


class EcommerceApiClient:
    """Cliente síncrono que trata la API como un consumidor externo."""

    def __init__(self, base_url: str, timeout: float) -> None:
        self._client = httpx.Client(
            base_url=base_url.rstrip("/") + "/",
            follow_redirects=False,
            headers={
                "Accept": "application/json",
                "User-Agent": "ecommerce-api-automation/0.1",
            },
            timeout=timeout,
        )

    def close(self) -> None:
        self._client.close()

    def request(
        self,
        method: str,
        path: str,
        *,
        headers: dict[str, str] | None = None,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> httpx.Response:
        normalized_path = path.lstrip("/")
        started_at = perf_counter()

        try:
            response = self._client.request(
                method,
                normalized_path,
                headers=headers,
                json=json,
                params=params,
            )
        except httpx.RequestError:
            logger.exception("%s %s | error de transporte", method, normalized_path)
            raise

        elapsed_ms = (perf_counter() - started_at) * 1_000
        logger.info(
            "%s %s | estado=%s | duracion_ms=%.1f",
            method.upper(),
            normalized_path,
            response.status_code,
            elapsed_ms,
        )
        return response

    def get(
        self,
        path: str,
        *,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
    ) -> httpx.Response:
        return self.request("GET", path, headers=headers, params=params)

    def post(
        self,
        path: str,
        *,
        headers: dict[str, str] | None = None,
        json: dict[str, Any] | None = None,
    ) -> httpx.Response:
        return self.request("POST", path, headers=headers, json=json)

    def patch(
        self,
        path: str,
        *,
        headers: dict[str, str] | None = None,
        json: dict[str, Any] | None = None,
    ) -> httpx.Response:
        return self.request("PATCH", path, headers=headers, json=json)

    def delete(
        self,
        path: str,
        *,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        return self.request("DELETE", path, headers=headers)
