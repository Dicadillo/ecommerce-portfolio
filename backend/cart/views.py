from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cart.models import CartItem
from cart.serializers import (
    AddCartItemSerializer,
    CartItemSerializer,
    CartSerializer,
    UpdateCartItemSerializer,
)
from cart.services import (
    add_product,
    get_active_cart,
    get_cart_with_items,
    update_item_quantity,
)
from config.openapi import (
    BAD_REQUEST_RESPONSE,
    NOT_FOUND_RESPONSE,
    UNAUTHORIZED_RESPONSE,
)


class CartDetailView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        tags=["Carrito"],
        summary="Consultar el carrito",
        description="Devuelve el carrito activo del usuario autenticado.",
        responses={200: CartSerializer, 401: UNAUTHORIZED_RESPONSE},
        examples=[
            OpenApiExample(
                "Carrito",
                value={
                    "id": 3,
                    "articulos": [
                        {
                            "id": 7,
                            "producto": 10,
                            "cantidad": 2,
                            "subtotal": "2599.80",
                        }
                    ],
                    "cantidad_total": 2,
                    "total": "2599.80",
                },
                response_only=True,
            )
        ],
    )
    def get(self, request):
        cart = get_active_cart(request.user)
        cart = get_cart_with_items(cart)
        return Response(CartSerializer(cart).data)


class CartItemListView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        tags=["Carrito"],
        summary="Añadir un producto al carrito",
        description=(
            "Añade el producto o incrementa la cantidad de su artículo existente. "
            "La cantidad total no puede superar el stock."
        ),
        request=AddCartItemSerializer,
        responses={
            200: CartItemSerializer,
            201: CartItemSerializer,
            400: BAD_REQUEST_RESPONSE,
            401: UNAUTHORIZED_RESPONSE,
        },
        examples=[
            OpenApiExample(
                "Producto y cantidad",
                value={"producto": 10, "cantidad": 2},
                request_only=True,
            ),
            OpenApiExample(
                "Artículo añadido",
                value={
                    "id": 7,
                    "producto": 10,
                    "cantidad": 2,
                    "subtotal": "2599.80",
                },
                response_only=True,
            ),
        ],
    )
    def post(self, request):
        serializer = AddCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cart = get_active_cart(request.user)
        item, created = add_product(cart=cart, **serializer.validated_data)
        response_status = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(CartItemSerializer(item).data, status=response_status)


class CartItemDetailView(APIView):
    permission_classes = (IsAuthenticated,)

    def get_item(self, request, item_id):
        return get_object_or_404(
            CartItem.objects.select_related("product"),
            pk=item_id,
            cart__user=request.user,
            cart__active=True,
        )

    @extend_schema(
        tags=["Carrito"],
        summary="Actualizar un artículo",
        description=(
            "Sustituye la cantidad de un artículo del carrito propio sin superar "
            "el stock disponible."
        ),
        request=UpdateCartItemSerializer,
        responses={
            200: CartItemSerializer,
            400: BAD_REQUEST_RESPONSE,
            401: UNAUTHORIZED_RESPONSE,
            404: NOT_FOUND_RESPONSE,
        },
        examples=[
            OpenApiExample(
                "Nueva cantidad",
                value={"cantidad": 3},
                request_only=True,
            ),
            OpenApiExample(
                "Artículo actualizado",
                value={
                    "id": 7,
                    "producto": 10,
                    "cantidad": 3,
                    "subtotal": "3899.70",
                },
                response_only=True,
            ),
        ],
    )
    def patch(self, request, item_id):
        item = self.get_item(request, item_id)
        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = update_item_quantity(item=item, **serializer.validated_data)
        return Response(CartItemSerializer(item).data)

    @extend_schema(
        tags=["Carrito"],
        summary="Eliminar un artículo",
        description="Elimina un artículo del carrito del usuario autenticado.",
        responses={
            204: None,
            401: UNAUTHORIZED_RESPONSE,
            404: NOT_FOUND_RESPONSE,
        },
    )
    def delete(self, request, item_id):
        item = self.get_item(request, item_id)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CartClearView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        tags=["Carrito"],
        summary="Vaciar el carrito",
        description="Elimina todos los artículos del carrito activo.",
        responses={204: None, 401: UNAUTHORIZED_RESPONSE},
    )
    def delete(self, request):
        cart = get_active_cart(request.user)
        cart.items.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
