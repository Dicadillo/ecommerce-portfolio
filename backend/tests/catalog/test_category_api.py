import pytest
from django.urls import reverse


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
