from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from config.openapi import (
    BAD_REQUEST_RESPONSE,
    NOT_FOUND_RESPONSE,
    UNAUTHORIZED_RESPONSE,
)
from payments.models import Payment
from payments.serializers import CreatePaymentSerializer, PaymentSerializer
from payments.services import create_payment, refund_payment

payment_example = {
    "id": 8,
    "pedido": 21,
    "estado": "aprobado",
    "importe": "2599.80",
    "referencia": "c665e417-f291-4d87-adac-740d84501593",
    "proveedor": "pasarela-simulada",
    "ultimos_cuatro": "1111",
    "fecha_creacion": "2026-01-15T10:05:00Z",
    "fecha_actualizacion": "2026-01-15T10:05:00Z",
}


def get_user_payment(user, payment_id):
    return get_object_or_404(
        Payment.objects.select_related("order"),
        pk=payment_id,
        order__user=user,
    )


class PaymentCreateView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        tags=["Pagos"],
        summary="Crear un pago simulado",
        description=(
            "Paga un pedido propio. La tarjeta 4111111111111111 aprueba, "
            "4000000000000002 rechaza y cualquier otra tarjeta válida deja el "
            "pago pendiente. Solo se conservan los últimos cuatro dígitos."
        ),
        request=CreatePaymentSerializer,
        responses={
            201: PaymentSerializer,
            400: BAD_REQUEST_RESPONSE,
            401: UNAUTHORIZED_RESPONSE,
            404: NOT_FOUND_RESPONSE,
        },
        examples=[
            OpenApiExample(
                "Pago que será aprobado",
                value={
                    "pedido": 21,
                    "numero_tarjeta": "4111111111111111",
                    "titular": "Santi García",
                    "fecha_expiracion": "12/30",
                    "cvv": "123",
                },
                request_only=True,
            ),
            OpenApiExample(
                "Pago creado",
                value=payment_example,
                response_only=True,
                status_codes=["201"],
            ),
        ],
    )
    def post(self, request):
        serializer = CreatePaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = create_payment(
            user=request.user,
            order_id=serializer.validated_data["order_id"],
            card_number=serializer.validated_data["card_number"],
        )
        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)


class PaymentDetailView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        tags=["Pagos"],
        summary="Consultar un pago",
        description="Devuelve un pago asociado a un pedido del usuario autenticado.",
        responses={
            200: PaymentSerializer,
            401: UNAUTHORIZED_RESPONSE,
            404: NOT_FOUND_RESPONSE,
        },
        examples=[
            OpenApiExample(
                "Detalle del pago",
                value=payment_example,
                response_only=True,
            )
        ],
    )
    def get(self, request, payment_id):
        payment = get_user_payment(request.user, payment_id)
        return Response(PaymentSerializer(payment).data)


class PaymentRefundView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        tags=["Pagos"],
        summary="Reembolsar un pago",
        description=(
            "Reembolsa un pago aprobado, cancela el pedido y devuelve el stock."
        ),
        request=None,
        responses={
            200: PaymentSerializer,
            400: BAD_REQUEST_RESPONSE,
            401: UNAUTHORIZED_RESPONSE,
            404: NOT_FOUND_RESPONSE,
        },
        examples=[
            OpenApiExample(
                "Pago reembolsado",
                value={**payment_example, "estado": "reembolsado"},
                response_only=True,
            )
        ],
    )
    def post(self, request, payment_id):
        payment = get_user_payment(request.user, payment_id)
        payment = refund_payment(payment)
        return Response(PaymentSerializer(payment).data)
