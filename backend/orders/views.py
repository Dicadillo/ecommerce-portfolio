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
from orders.models import Order
from orders.serializers import CreateOrderSerializer, OrderSerializer
from orders.services import cancel_order, create_order_from_cart, get_order_with_items

order_example = {
    "id": 21,
    "estado": "pendiente",
    "nombre_destinatario": "Santi García",
    "direccion": "Calle Mayor 10",
    "ciudad": "Madrid",
    "codigo_postal": "28013",
    "pais": "España",
    "total": "2599.80",
    "fecha_creacion": "2026-01-15T10:00:00Z",
    "fecha_actualizacion": "2026-01-15T10:00:00Z",
    "articulos": [
        {
            "id": 31,
            "producto": 10,
            "nombre_producto": "Portátil QA",
            "precio_unitario": "1299.90",
            "cantidad": 2,
            "subtotal": "2599.80",
        }
    ],
}


def get_user_order(user, order_id):
    order = get_object_or_404(Order, pk=order_id, user=user)
    return get_order_with_items(order)


class OrderListCreateView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        tags=["Pedidos"],
        summary="Listar pedidos",
        description="Devuelve únicamente los pedidos del usuario autenticado.",
        responses={200: OrderSerializer(many=True), 401: UNAUTHORIZED_RESPONSE},
        examples=[
            OpenApiExample(
                "Pedidos propios",
                value=[order_example],
                response_only=True,
            )
        ],
    )
    def get(self, request):
        orders = Order.objects.filter(user=request.user).prefetch_related("items")
        return Response(OrderSerializer(orders, many=True).data)

    @extend_schema(
        tags=["Pedidos"],
        summary="Crear un pedido",
        description=(
            "Crea un pedido pendiente desde el carrito activo, comprueba y reduce "
            "el stock de forma atómica y vacía el carrito."
        ),
        request=CreateOrderSerializer,
        responses={
            201: OrderSerializer,
            400: BAD_REQUEST_RESPONSE,
            401: UNAUTHORIZED_RESPONSE,
        },
        examples=[
            OpenApiExample(
                "Datos de entrega",
                value={
                    "nombre_destinatario": "Santi García",
                    "direccion": "Calle Mayor 10",
                    "ciudad": "Madrid",
                    "codigo_postal": "28013",
                    "pais": "España",
                },
                request_only=True,
            ),
            OpenApiExample(
                "Pedido creado",
                value=order_example,
                response_only=True,
                status_codes=["201"],
            ),
        ],
    )
    def post(self, request):
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = create_order_from_cart(
            user=request.user,
            delivery_data=serializer.validated_data,
        )
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderDetailView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        tags=["Pedidos"],
        summary="Consultar un pedido",
        description="Devuelve un pedido propio y su copia histórica de artículos.",
        responses={
            200: OrderSerializer,
            401: UNAUTHORIZED_RESPONSE,
            404: NOT_FOUND_RESPONSE,
        },
        examples=[
            OpenApiExample(
                "Detalle del pedido",
                value=order_example,
                response_only=True,
            )
        ],
    )
    def get(self, request, order_id):
        order = get_user_order(request.user, order_id)
        return Response(OrderSerializer(order).data)


class OrderCancelView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        tags=["Pedidos"],
        summary="Cancelar un pedido",
        description=(
            "Cancela un pedido pendiente o confirmado y devuelve sus unidades al stock."
        ),
        request=None,
        responses={
            200: OrderSerializer,
            400: BAD_REQUEST_RESPONSE,
            401: UNAUTHORIZED_RESPONSE,
            404: NOT_FOUND_RESPONSE,
        },
        examples=[
            OpenApiExample(
                "Pedido cancelado",
                value={**order_example, "estado": "cancelado"},
                response_only=True,
            )
        ],
    )
    def post(self, request, order_id):
        order = get_user_order(request.user, order_id)
        order = cancel_order(order)
        return Response(OrderSerializer(order).data)
