from drf_spectacular.utils import OpenApiExample, OpenApiResponse
from rest_framework import serializers


class ErrorContentSerializer(serializers.Serializer):
    codigo = serializers.CharField(
        help_text="Código estable y procesable del error.",
    )
    mensaje = serializers.CharField(
        help_text="Explicación legible del error.",
    )
    detalles = serializers.DictField(
        help_text="Errores por campo o información adicional.",
    )


class ErrorSerializer(serializers.Serializer):
    error = ErrorContentSerializer()


BAD_REQUEST_RESPONSE = OpenApiResponse(
    response=ErrorSerializer,
    description="Error de validación o incumplimiento de una regla de negocio.",
    examples=[
        OpenApiExample(
            "Validación incorrecta",
            value={
                "error": {
                    "codigo": "validacion_incorrecta",
                    "mensaje": "La solicitud contiene datos no válidos.",
                    "detalles": {"campo": ["Mensaje de validación."]},
                }
            },
            response_only=True,
        ),
        OpenApiExample(
            "Regla de negocio",
            value={
                "error": {
                    "codigo": "regla_de_negocio",
                    "mensaje": "La operación incumple una regla de negocio.",
                    "detalles": {"recurso": "La operación no está permitida."},
                }
            },
            response_only=True,
        ),
    ],
)
UNAUTHORIZED_RESPONSE = OpenApiResponse(
    response=ErrorSerializer,
    description="No se proporcionó un token JWT válido.",
    examples=[
        OpenApiExample(
            "Autenticación requerida",
            value={
                "error": {
                    "codigo": "autenticacion_requerida",
                    "mensaje": "Debes autenticarte para acceder a este recurso.",
                    "detalles": {},
                }
            },
            response_only=True,
        )
    ],
)
NOT_FOUND_RESPONSE = OpenApiResponse(
    response=ErrorSerializer,
    description="El recurso no existe o no pertenece al usuario autenticado.",
    examples=[
        OpenApiExample(
            "Recurso no encontrado",
            value={
                "error": {
                    "codigo": "recurso_no_encontrado",
                    "mensaje": "El recurso solicitado no existe.",
                    "detalles": {},
                }
            },
            response_only=True,
        )
    ],
)
