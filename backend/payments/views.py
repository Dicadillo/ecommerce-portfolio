from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from payments.models import Payment
from payments.serializers import CreatePaymentSerializer, PaymentSerializer
from payments.services import create_payment, refund_payment


def get_user_payment(user, payment_id):
    return get_object_or_404(
        Payment.objects.select_related("order"),
        pk=payment_id,
        order__user=user,
    )


class PaymentCreateView(APIView):
    permission_classes = (IsAuthenticated,)

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

    def get(self, request, payment_id):
        payment = get_user_payment(request.user, payment_id)
        return Response(PaymentSerializer(payment).data)


class PaymentRefundView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, payment_id):
        payment = get_user_payment(request.user, payment_id)
        payment = refund_payment(payment)
        return Response(PaymentSerializer(payment).data)
