from collections.abc import Mapping

from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import (
    APIException,
    AuthenticationFailed,
    MethodNotAllowed,
    NotAuthenticated,
    NotFound,
    ParseError,
    PermissionDenied,
    Throttled,
    ValidationError,
)
from rest_framework.response import Response
from rest_framework.views import exception_handler

from config.exceptions import AuthenticationError, BusinessRuleError

ERROR_PROFILES = (
    (
        BusinessRuleError,
        "regla_de_negocio",
        "La operación incumple una regla de negocio.",
    ),
    (
        ValidationError,
        "validacion_incorrecta",
        "La solicitud contiene datos no válidos.",
    ),
    (
        AuthenticationError,
        "autenticacion_fallida",
        "No se pudo validar la autenticación.",
    ),
    (
        NotAuthenticated,
        "autenticacion_requerida",
        "Debes autenticarte para acceder a este recurso.",
    ),
    (
        AuthenticationFailed,
        "autenticacion_fallida",
        "No se pudo validar la autenticación.",
    ),
    (
        (DjangoPermissionDenied, PermissionDenied),
        "permiso_denegado",
        "No tienes permisos para realizar esta operación.",
    ),
    (
        (Http404, NotFound),
        "recurso_no_encontrado",
        "El recurso solicitado no existe.",
    ),
    (
        MethodNotAllowed,
        "metodo_no_permitido",
        "El método HTTP no está permitido para este recurso.",
    ),
    (ParseError, "solicitud_mal_formada", "No se pudo interpretar la solicitud."),
    (
        Throttled,
        "limite_solicitudes",
        "Se ha superado temporalmente el límite de solicitudes.",
    ),
)


def _plain_value(value):
    if isinstance(value, Mapping):
        return {str(key): _plain_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain_value(item) for item in value]
    return str(value)


def _error_profile(exception):
    for exception_type, code, message in ERROR_PROFILES:
        if isinstance(exception, exception_type):
            return code, message
    if isinstance(exception, APIException):
        return "error_api", "No se pudo completar la solicitud."
    return "error_interno", "Se produjo un error interno."


def _error_details(data):
    plain_data = _plain_value(data)
    if not isinstance(plain_data, dict):
        return {"errores": plain_data}

    return {
        key: value
        for key, value in plain_data.items()
        if key not in {"detail", "detalle", "code", "messages"}
    }


def api_exception_handler(exception, context):
    response = exception_handler(exception, context)
    code, message = _error_profile(exception)
    details = _error_details(response.data) if response is not None else {}
    status_code = (
        response.status_code
        if response is not None
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    headers = dict(response.items()) if response is not None else None

    return Response(
        {
            "error": {
                "codigo": code,
                "mensaje": message,
                "detalles": details,
            }
        },
        status=status_code,
        headers=headers,
    )
