from django.urls import path

from payments.views import PaymentCreateView, PaymentDetailView, PaymentRefundView

urlpatterns = [
    path("", PaymentCreateView.as_view(), name="payment-create"),
    path("<int:payment_id>/", PaymentDetailView.as_view(), name="payment-detail"),
    path(
        "<int:payment_id>/reembolsar/",
        PaymentRefundView.as_view(),
        name="payment-refund",
    ),
]
