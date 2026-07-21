import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from tests.users.conftest import VALID_PASSWORD

User = get_user_model()


def registration_payload(**overrides):
    values = {
        "usuario": "newuser",
        "correo": "newuser@example.com",
        "contrasena": VALID_PASSWORD,
        "confirmacion_contrasena": VALID_PASSWORD,
    }
    values.update(overrides)
    return values


def login(api_client, username="testuser", password=VALID_PASSWORD):
    return api_client.post(
        reverse("login"),
        {"usuario": username, "contrasena": password},
        format="json",
    )


@pytest.mark.django_db
def test_successful_registration(api_client):
    response = api_client.post(
        reverse("register"),
        registration_payload(),
        format="json",
    )

    assert response.status_code == 201
    assert set(response.data) == {"id", "usuario", "correo"}
    assert response.data["usuario"] == "newuser"
    assert response.data["correo"] == "newuser@example.com"

    user = User.objects.get(username="newuser")
    assert user.check_password(VALID_PASSWORD)


@pytest.mark.django_db
def test_registration_rejects_duplicate_username(api_client, user_factory):
    user_factory(username="newuser")

    response = api_client.post(
        reverse("register"),
        registration_payload(),
        format="json",
    )

    assert response.status_code == 400
    assert "usuario" in response.data


@pytest.mark.django_db
def test_registration_rejects_invalid_email(api_client):
    response = api_client.post(
        reverse("register"),
        registration_payload(correo="invalid-email"),
        format="json",
    )

    assert response.status_code == 400
    assert "correo" in response.data


@pytest.mark.django_db
def test_registration_rejects_different_passwords(api_client):
    response = api_client.post(
        reverse("register"),
        registration_payload(confirmacion_contrasena="DifferentPass!123"),
        format="json",
    )

    assert response.status_code == 400
    assert "confirmacion_contrasena" in response.data


@pytest.mark.django_db
def test_registration_uses_django_password_validators(api_client):
    response = api_client.post(
        reverse("register"),
        registration_payload(contrasena="123", confirmacion_contrasena="123"),
        format="json",
    )

    assert response.status_code == 400
    assert "contrasena" in response.data


@pytest.mark.django_db
def test_successful_login_returns_token_pair(api_client, user_factory):
    user_factory()

    response = login(api_client)

    assert response.status_code == 200
    assert set(response.data) == {"acceso", "refresco"}
    AccessToken(response.data["acceso"])
    RefreshToken(response.data["refresco"])


@pytest.mark.django_db
def test_incorrect_login_returns_unauthorized(api_client, user_factory):
    user_factory()

    response = login(api_client, password="WrongPass!123")

    assert response.status_code == 401
    assert "detalle" in response.data


@pytest.mark.django_db
def test_refresh_token_returns_new_access_token(api_client, user_factory):
    user_factory()
    login_response = login(api_client)

    response = api_client.post(
        reverse("token-refresh"),
        {"refresco": login_response.data["refresco"]},
        format="json",
    )

    assert response.status_code == 200
    assert set(response.data) == {"acceso"}
    AccessToken(response.data["acceso"])


@pytest.mark.django_db
def test_authenticated_profile_returns_user(api_client, user_factory):
    user = user_factory()
    login_response = login(api_client)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_response.data['acceso']}")

    response = api_client.get(reverse("profile"))

    assert response.status_code == 200
    assert response.data == {
        "id": user.id,
        "usuario": user.username,
        "correo": user.email,
    }


@pytest.mark.django_db
def test_profile_without_authentication_returns_unauthorized(api_client):
    response = api_client.get(reverse("profile"))

    assert response.status_code == 401
    assert "detalle" in response.data


@pytest.mark.django_db
def test_logout_blacklists_refresh_token(api_client, user_factory):
    user_factory()
    login_response = login(api_client)
    access = login_response.data["acceso"]
    refresh = login_response.data["refresco"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    logout_response = api_client.post(
        reverse("logout"),
        {"refresco": refresh},
        format="json",
    )

    assert logout_response.status_code == 204

    refresh_response = api_client.post(
        reverse("token-refresh"),
        {"refresco": refresh},
        format="json",
    )
    assert refresh_response.status_code == 400
