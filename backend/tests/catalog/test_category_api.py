import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken

from tests.assertions import assert_error_response


@pytest.mark.django_db
def test_category_list_is_paginated(api_client, category_factory):
    category_factory(name="Books", slug="books")
    category_factory(name="Electronics", slug="electronics")

    response = api_client.get(reverse("category-list"))

    assert response.status_code == 200
    assert response.data["conteo"] == 2
    assert response.data["siguiente"] is None
    assert response.data["anterior"] is None
    assert [item["nombre"] for item in response.data["resultados"]] == [
        "Books",
        "Electronics",
    ]


@pytest.mark.django_db
def test_category_detail_returns_requested_category(api_client, category_factory):
    category = category_factory(name="Electronics", slug="electronics")

    response = api_client.get(reverse("category-detail", args=[category.id]))

    assert response.status_code == 200
    assert response.data["id"] == category.id
    assert response.data["nombre"] == "Electronics"
    assert response.data["slug"] == "electronics"


@pytest.mark.django_db
def test_catalog_is_read_only_for_regular_users(
    api_client,
    category_factory,
    product_factory,
):
    user = get_user_model().objects.create_user(
        username="catalog-reader",
        password="SecurePass!123",
    )
    token = RefreshToken.for_user(user).access_token
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    category = category_factory()
    product = product_factory(category=category)

    responses = (
        api_client.post(reverse("category-list"), {"nombre": "Nueva"}),
        api_client.patch(reverse("category-detail", args=[category.id]), {}),
        api_client.delete(reverse("category-detail", args=[category.id])),
        api_client.post(reverse("product-list"), {"nombre": "Nuevo"}),
        api_client.patch(reverse("product-detail", args=[product.id]), {}),
        api_client.delete(reverse("product-detail", args=[product.id])),
    )

    for response in responses:
        assert response.status_code == 405
        assert_error_response(response, "metodo_no_permitido")


@pytest.mark.django_db
def test_public_catalog_ignores_an_invalid_bearer_token(api_client):
    api_client.credentials(HTTP_AUTHORIZATION="Bearer token-no-valido")

    category_response = api_client.get(reverse("category-list"))
    product_response = api_client.get(reverse("product-list"))

    assert category_response.status_code == 200
    assert product_response.status_code == 200


@pytest.mark.django_db
def test_category_detail_returns_uniform_not_found_error(api_client):
    response = api_client.get(reverse("category-detail", args=[999999]))

    assert response.status_code == 404
    assert_error_response(response, "recurso_no_encontrado")
