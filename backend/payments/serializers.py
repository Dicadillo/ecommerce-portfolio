from rest_framework import serializers

from payments.models import Payment
from payments.validators import validate_card_data


class PaymentSerializer(serializers.ModelSerializer):
    pedido = serializers.IntegerField(source="order_id", read_only=True)
    estado = serializers.CharField(source="status", read_only=True)
    importe = serializers.DecimalField(
        source="amount",
        max_digits=18,
        decimal_places=2,
        read_only=True,
    )
    referencia = serializers.UUIDField(source="reference", read_only=True)
    proveedor = serializers.CharField(source="provider", read_only=True)
    ultimos_cuatro = serializers.CharField(
        source="card_last_four",
        read_only=True,
    )
    fecha_creacion = serializers.DateTimeField(source="created_at", read_only=True)
    fecha_actualizacion = serializers.DateTimeField(
        source="updated_at",
        read_only=True,
    )

    class Meta:
        model = Payment
        fields = (
            "id",
            "pedido",
            "estado",
            "importe",
            "referencia",
            "proveedor",
            "ultimos_cuatro",
            "fecha_creacion",
            "fecha_actualizacion",
        )
        read_only_fields = fields


class CreatePaymentSerializer(serializers.Serializer):
    pedido = serializers.IntegerField(source="order_id", min_value=1)
    numero_tarjeta = serializers.CharField(
        source="card_number",
        max_length=25,
        write_only=True,
        trim_whitespace=False,
    )
    titular = serializers.CharField(
        source="cardholder",
        max_length=200,
        write_only=True,
    )
    fecha_expiracion = serializers.CharField(
        source="expiration_date",
        max_length=5,
        write_only=True,
    )
    cvv = serializers.CharField(
        max_length=4,
        write_only=True,
        trim_whitespace=False,
    )

    def validate(self, attributes):
        attributes["card_number"] = validate_card_data(
            card_number=attributes["card_number"],
            expiration_date=attributes["expiration_date"],
            cvv=attributes["cvv"],
        )
        return attributes
