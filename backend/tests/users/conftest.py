import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()

VALID_PASSWORD = "SecurePass!123"


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_factory(db):
    def create_user(**overrides):
        values = {
            "username": "testuser",
            "email": "test@example.com",
            "password": VALID_PASSWORD,
        }
        values.update(overrides)
        return User.objects.create_user(**values)

    return create_user
