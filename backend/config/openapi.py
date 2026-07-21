from drf_spectacular.utils import OpenApiResponse
from rest_framework import serializers


class ErrorSerializer(serializers.Serializer):
    detalle = serializers.CharField(
        help_text="Descripción del error.",
    )


VALIDATION_ERROR_SCHEMA = {
    "type": "object",
    "additionalProperties": {
        "oneOf": [
            {"type": "string"},
            {"type": "array", "items": {"type": "string"}},
        ]
    },
    "example": {"campo": ["Mensaje de validación."]},
}

BAD_REQUEST_RESPONSE = OpenApiResponse(
    response=VALIDATION_ERROR_SCHEMA,
    description="La solicitud contiene datos no válidos o incumple una regla.",
)
UNAUTHORIZED_RESPONSE = OpenApiResponse(
    response=ErrorSerializer,
    description="No se proporcionó un token JWT válido.",
)
NOT_FOUND_RESPONSE = OpenApiResponse(
    response=ErrorSerializer,
    description="El recurso no existe o no pertenece al usuario autenticado.",
)
