from rest_framework import serializers

from cart.models import Cart, CartItem
from cart.services import validate_product
from catalog.models import Product


class CartItemSerializer(serializers.ModelSerializer):
    producto = serializers.PrimaryKeyRelatedField(
        source="product",
        read_only=True,
    )
    cantidad = serializers.IntegerField(source="quantity", read_only=True)
    subtotal = serializers.DecimalField(
        max_digits=18,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = CartItem
        fields = ("id", "producto", "cantidad", "subtotal")
        read_only_fields = fields


class CartSerializer(serializers.ModelSerializer):
    articulos = CartItemSerializer(source="items", many=True, read_only=True)
    cantidad_total = serializers.IntegerField(source="total_items", read_only=True)
    total = serializers.DecimalField(
        max_digits=18,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = Cart
        fields = ("id", "articulos", "cantidad_total", "total")
        read_only_fields = fields


class AddCartItemSerializer(serializers.Serializer):
    producto = serializers.PrimaryKeyRelatedField(
        source="product",
        queryset=Product.objects.all(),
        error_messages={
            "does_not_exist": "El producto no existe.",
            "incorrect_type": "El producto debe ser un identificador entero.",
        },
    )
    cantidad = serializers.IntegerField(
        source="quantity",
        min_value=1,
        error_messages={
            "invalid": "La cantidad debe ser un número entero.",
            "min_value": "La cantidad debe ser mayor que cero.",
        },
    )

    def validate(self, attributes):
        validate_product(attributes["product"], attributes["quantity"])
        return attributes


class UpdateCartItemSerializer(serializers.Serializer):
    cantidad = serializers.IntegerField(
        source="quantity",
        min_value=1,
        error_messages={
            "invalid": "La cantidad debe ser un número entero.",
            "min_value": "La cantidad debe ser mayor que cero.",
        },
    )
