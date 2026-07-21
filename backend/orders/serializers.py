from rest_framework import serializers

from orders.models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    producto = serializers.IntegerField(
        source="product_id",
        allow_null=True,
        read_only=True,
    )
    nombre_producto = serializers.CharField(
        source="product_name",
        read_only=True,
    )
    precio_unitario = serializers.DecimalField(
        source="unit_price",
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )
    cantidad = serializers.IntegerField(source="quantity", read_only=True)

    class Meta:
        model = OrderItem
        fields = (
            "id",
            "producto",
            "nombre_producto",
            "precio_unitario",
            "cantidad",
            "subtotal",
        )
        read_only_fields = fields


class OrderSerializer(serializers.ModelSerializer):
    estado = serializers.CharField(source="status", read_only=True)
    nombre_destinatario = serializers.CharField(
        source="recipient_name",
        read_only=True,
    )
    direccion = serializers.CharField(source="address", read_only=True)
    ciudad = serializers.CharField(source="city", read_only=True)
    codigo_postal = serializers.CharField(source="postal_code", read_only=True)
    pais = serializers.CharField(source="country", read_only=True)
    fecha_creacion = serializers.DateTimeField(source="created_at", read_only=True)
    fecha_actualizacion = serializers.DateTimeField(
        source="updated_at",
        read_only=True,
    )
    articulos = OrderItemSerializer(source="items", many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "estado",
            "nombre_destinatario",
            "direccion",
            "ciudad",
            "codigo_postal",
            "pais",
            "total",
            "fecha_creacion",
            "fecha_actualizacion",
            "articulos",
        )
        read_only_fields = fields


class CreateOrderSerializer(serializers.Serializer):
    nombre_destinatario = serializers.CharField(
        source="recipient_name",
        max_length=200,
    )
    direccion = serializers.CharField(source="address")
    ciudad = serializers.CharField(source="city", max_length=120)
    codigo_postal = serializers.CharField(source="postal_code", max_length=20)
    pais = serializers.CharField(source="country", max_length=100)
