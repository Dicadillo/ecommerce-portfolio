from decimal import Decimal
from itertools import count

import pytest
from rest_framework.test import APIClient

from catalog.models import Category, Product


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def category_factory(db):
    sequence = count(1)

    def create_category(**overrides):
        number = next(sequence)
        values = {
            "name": f"Category {number}",
            "slug": f"category-{number}",
            "active": True,
        }
        values.update(overrides)
        return Category.objects.create(**values)

    return create_category


@pytest.fixture
def product_factory(db, category_factory):
    sequence = count(1)

    def create_product(**overrides):
        number = next(sequence)
        category = overrides.pop("category", None) or category_factory()
        values = {
            "category": category,
            "name": f"Product {number}",
            "slug": f"product-{number}",
            "description": f"Description {number}",
            "price": Decimal("10.00"),
            "stock": 5,
            "active": True,
        }
        values.update(overrides)
        return Product.objects.create(**values)

    return create_product
