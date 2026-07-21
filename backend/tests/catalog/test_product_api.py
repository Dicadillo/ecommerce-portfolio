from decimal import Decimal

import pytest
from django.urls import reverse

from tests.assertions import assert_error_response


def response_names(response):
    return [item["nombre"] for item in response.data["resultados"]]


@pytest.mark.django_db
def test_product_list_is_paginated(api_client, product_factory):
    product_factory(name="Keyboard", slug="keyboard")
    product_factory(name="Mouse", slug="mouse")

    response = api_client.get(reverse("product-list"))

    assert response.status_code == 200
    assert response.data["conteo"] == 2
    assert response_names(response) == ["Keyboard", "Mouse"]


@pytest.mark.django_db
def test_product_detail_returns_requested_product(api_client, product_factory):
    product = product_factory(
        name="Keyboard",
        slug="keyboard",
        price=Decimal("49.90"),
    )

    response = api_client.get(reverse("product-detail", args=[product.id]))

    assert response.status_code == 200
    assert response.data["id"] == product.id
    assert response.data["nombre"] == "Keyboard"
    assert response.data["precio"] == "49.90"


@pytest.mark.django_db
def test_product_list_filters_by_category(
    api_client,
    category_factory,
    product_factory,
):
    electronics = category_factory(name="Electronics", slug="electronics")
    books = category_factory(name="Books", slug="books")
    product_factory(category=electronics, name="Keyboard", slug="keyboard")
    product_factory(category=books, name="Novel", slug="novel")

    response = api_client.get(
        reverse("product-list"),
        {"categoria": electronics.id},
    )

    assert response.status_code == 200
    assert response_names(response) == ["Keyboard"]


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("active", "expected_name"),
    (("true", "Active product"), ("false", "Inactive product")),
)
def test_product_list_filters_by_active(
    active,
    expected_name,
    api_client,
    product_factory,
):
    product_factory(name="Active product", slug="active", active=True)
    product_factory(name="Inactive product", slug="inactive", active=False)

    response = api_client.get(reverse("product-list"), {"activo": active})

    assert response.status_code == 200
    assert response_names(response) == [expected_name]


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("in_stock", "expected_name"),
    (("true", "Available product"), ("false", "Sold out product")),
)
def test_product_list_filters_by_stock(
    in_stock,
    expected_name,
    api_client,
    product_factory,
):
    product_factory(name="Available product", slug="available", stock=4)
    product_factory(name="Sold out product", slug="sold-out", stock=0)

    response = api_client.get(reverse("product-list"), {"con_stock": in_stock})

    assert response.status_code == 200
    assert response_names(response) == [expected_name]


@pytest.mark.django_db
def test_product_list_searches_by_name(api_client, product_factory):
    product_factory(name="Mechanical keyboard", slug="keyboard")
    product_factory(name="Wireless mouse", slug="mouse")

    response = api_client.get(reverse("product-list"), {"buscar": "keyboard"})

    assert response.status_code == 200
    assert response_names(response) == ["Mechanical keyboard"]


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("ordering", "expected_names"),
    (
        ("nombre", ["Keyboard", "Mouse"]),
        ("-nombre", ["Mouse", "Keyboard"]),
        ("precio", ["Mouse", "Keyboard"]),
        ("-precio", ["Keyboard", "Mouse"]),
    ),
)
def test_product_list_orders_by_public_fields(
    ordering,
    expected_names,
    api_client,
    product_factory,
):
    product_factory(name="Keyboard", slug="keyboard", price=Decimal("50.00"))
    product_factory(name="Mouse", slug="mouse", price=Decimal("20.00"))

    response = api_client.get(reverse("product-list"), {"ordenar": ordering})

    assert response.status_code == 200
    assert response_names(response) == expected_names


@pytest.mark.django_db
def test_product_list_supports_custom_page_size(api_client, product_factory):
    for number in range(3):
        product_factory(name=f"Product {number}", slug=f"product-page-{number}")

    response = api_client.get(reverse("product-list"), {"tamano_pagina": 2})

    assert response.status_code == 200
    assert response.data["conteo"] == 3
    assert len(response.data["resultados"]) == 2
    assert response.data["siguiente"] is not None


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("parameters", "detail_field"),
    (
        ({"categoria": "abc"}, "categoria"),
        ({"categoria": 0}, "categoria"),
        ({"activo": "quizas"}, "activo"),
        ({"con_stock": "quizas"}, "con_stock"),
        ({"ordenar": "stock"}, "ordenar"),
        ({"tamano_pagina": "abc"}, "tamano_pagina"),
        ({"tamano_pagina": 0}, "tamano_pagina"),
    ),
)
def test_product_list_rejects_invalid_query_parameters(
    parameters,
    detail_field,
    api_client,
):
    response = api_client.get(reverse("product-list"), parameters)

    assert response.status_code == 400
    assert_error_response(response, "validacion_incorrecta", detail_field)


@pytest.mark.django_db
def test_product_detail_returns_uniform_not_found_error(api_client):
    response = api_client.get(reverse("product-detail", args=[999999]))

    assert response.status_code == 404
    assert_error_response(response, "recurso_no_encontrado")
