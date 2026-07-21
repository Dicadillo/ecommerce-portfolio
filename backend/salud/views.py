from drf_spectacular.utils import OpenApiExample, extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

health_response_serializer = inline_serializer(
    name="RespuestaSalud",
    fields={"status": serializers.CharField()},
)


@extend_schema(
    tags=["Salud"],
    summary="Comprobar el estado de la API",
    description="Confirma que el backend está disponible.",
    responses={200: health_response_serializer},
    auth=[],
    examples=[
        OpenApiExample(
            "API disponible",
            value={"status": "ok"},
            response_only=True,
        )
    ],
)
@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def comprobar_salud(solicitud):
    return Response({"status": "ok"})
