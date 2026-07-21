from django.shortcuts import get_object_or_404
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


class CartDetailView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        cart = get_active_cart(request.user)
        cart = get_cart_with_items(cart)
        return Response(CartSerializer(cart).data)


class CartItemListView(APIView):
    permission_classes = (IsAuthenticated,)

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

    def patch(self, request, item_id):
        item = self.get_item(request, item_id)
        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = update_item_quantity(item=item, **serializer.validated_data)
        return Response(CartItemSerializer(item).data)

    def delete(self, request, item_id):
        item = self.get_item(request, item_id)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CartClearView(APIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request):
        cart = get_active_cart(request.user)
        cart.items.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
