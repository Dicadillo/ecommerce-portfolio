from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models import Order
from orders.serializers import CreateOrderSerializer, OrderSerializer
from orders.services import cancel_order, create_order_from_cart, get_order_with_items


def get_user_order(user, order_id):
    order = get_object_or_404(Order, pk=order_id, user=user)
    return get_order_with_items(order)


class OrderListCreateView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        orders = Order.objects.filter(user=request.user).prefetch_related("items")
        return Response(OrderSerializer(orders, many=True).data)

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

    def get(self, request, order_id):
        order = get_user_order(request.user, order_id)
        return Response(OrderSerializer(order).data)


class OrderCancelView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, order_id):
        order = get_user_order(request.user, order_id)
        order = cancel_order(order)
        return Response(OrderSerializer(order).data)
