from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from catalog.models import Category, Product


def test_category_defaults_and_string_representation(category_factory):
    category = category_factory(name="Electronics")

    assert category.active is True
    assert category.created_at is not None
    assert category.updated_at is not None
    assert str(category) == "Electronics"


def test_product_fields_and_string_representation(product_factory):
    product = product_factory(
        name="Keyboard",
        price=Decimal("49.90"),
        stock=8,
    )

    assert product.category_id is not None
    assert product.price == Decimal("49.90")
    assert product.stock == 8
    assert product.active is True
    assert product.created_at is not None
    assert product.updated_at is not None
    assert str(product) == "Keyboard"


def test_category_slug_must_be_unique(category_factory):
    category_factory(slug="electronics")
    duplicate = Category(name="Other", slug="electronics")

    with pytest.raises(ValidationError) as error:
        duplicate.full_clean()

    assert "slug" in error.value.message_dict


def test_product_slug_must_be_unique(product_factory, category_factory):
    product_factory(slug="keyboard")
    duplicate = Product(
        category=category_factory(),
        name="Other keyboard",
        slug="keyboard",
        price=Decimal("1.00"),
        stock=1,
    )

    with pytest.raises(ValidationError) as error:
        duplicate.full_clean()

    assert "slug" in error.value.message_dict


@pytest.mark.parametrize(
    ("field", "value"),
    (("price", Decimal("-0.01")), ("stock", -1)),
)
def test_product_rejects_negative_price_and_stock(
    field,
    value,
    category_factory,
):
    values = {
        "category": category_factory(),
        "name": "Invalid product",
        "slug": f"invalid-{field}",
        "price": Decimal("10.00"),
        "stock": 1,
    }
    values[field] = value
    product = Product(**values)

    with pytest.raises(ValidationError) as error:
        product.full_clean()

    assert field in error.value.message_dict
