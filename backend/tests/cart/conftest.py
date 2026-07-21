from decimal import Decimal
from itertools import count

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from catalog.models import Category, Product

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_factory(db):
    sequence = count(1)

    def create_user(**overrides):
        number = next(sequence)
        values = {
            "username": f"cart-user-{number}",
            "email": f"cart-user-{number}@example.com",
            "password": "SecurePass!123",
        }
        values.update(overrides)
        return User.objects.create_user(**values)

    return create_user


@pytest.fixture
def user(user_factory):
    return user_factory()


def authenticate_client(client, user):
    access = RefreshToken.for_user(user).access_token
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    return client


@pytest.fixture
def authenticated_client(api_client, user):
    return authenticate_client(api_client, user)


@pytest.fixture
def product_factory(db):
    sequence = count(1)
    category = Category.objects.create(name="Cart category", slug="cart-category")

    def create_product(**overrides):
        number = next(sequence)
        values = {
            "category": category,
            "name": f"Cart product {number}",
            "slug": f"cart-product-{number}",
            "description": "Product for cart tests",
            "price": Decimal("10.00"),
            "stock": 10,
            "active": True,
        }
        values.update(overrides)
        return Product.objects.create(**values)

    return create_product
