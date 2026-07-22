import pytest

from clients.api_client import EcommerceApiClient
from helpers.assertions import assert_status


@pytest.mark.smoke
def test_health_endpoint_reports_ok(api_client: EcommerceApiClient) -> None:
    response = api_client.get("salud/")

    assert_status(response, 200)
    assert response.json() == {"status": "ok"}
