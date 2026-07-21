import pytest
from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.test import override_settings
from django.urls import path, reverse
from rest_framework.exceptions import (
    APIException,
    MethodNotAllowed,
    ParseError,
    PermissionDenied,
    Throttled,
    ValidationError,
)
from rest_framework.permissions import AllowAny
from rest_framework.test import APIClient
from rest_framework.views import APIView

from config.exception_handlers import api_exception_handler
from tests.assertions import assert_error_response


class CrashingView(APIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)

    def get(self, request):
        raise RuntimeError("dato-interno-sensible")


urlpatterns = [path("error-interno/", CrashingView.as_view())]


@pytest.mark.parametrize(
    ("exception", "status_code", "code"),
    (
        (PermissionDenied(), 403, "permiso_denegado"),
        (DjangoPermissionDenied(), 403, "permiso_denegado"),
        (MethodNotAllowed("POST"), 405, "metodo_no_permitido"),
        (ParseError(), 400, "solicitud_mal_formada"),
        (Throttled(wait=1), 429, "limite_solicitudes"),
        (APIException(), 500, "error_api"),
    ),
)
def test_api_exceptions_use_the_uniform_format(exception, status_code, code):
    response = api_exception_handler(exception, {})

    assert response.status_code == status_code
    assert_error_response(response, code)


def test_list_validation_errors_are_placed_in_details():
    response = api_exception_handler(ValidationError(["Dato no válido."]), {})

    error = assert_error_response(response, "validacion_incorrecta")
    assert error["detalles"] == {"errores": ["Dato no válido."]}


def test_malformed_json_uses_the_uniform_format():
    response = APIClient().post(
        reverse("register"),
        data='{"usuario":',
        content_type="application/json",
    )

    assert response.status_code == 400
    assert_error_response(response, "solicitud_mal_formada")


def test_invalid_jwt_uses_the_uniform_format():
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION="Bearer token-no-valido")

    response = client.get(reverse("cart-detail"))

    assert response.status_code == 401
    assert_error_response(response, "autenticacion_fallida")


@override_settings(ROOT_URLCONF=__name__, DEBUG=False)
def test_unhandled_exceptions_do_not_expose_internal_details():
    response = APIClient().get("/error-interno/")

    assert response.status_code == 500
    assert_error_response(response, "error_interno")
    assert "dato-interno-sensible" not in response.content.decode()
