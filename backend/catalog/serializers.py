from rest_framework import serializers

from catalog.models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    nombre = serializers.CharField(source="name", read_only=True)
    activo = serializers.BooleanField(source="active", read_only=True)
    creado_en = serializers.DateTimeField(source="created_at", read_only=True)
    actualizado_en = serializers.DateTimeField(source="updated_at", read_only=True)

    class Meta:
        model = Category
        fields = (
            "id",
            "nombre",
            "slug",
            "activo",
            "creado_en",
            "actualizado_en",
        )
        read_only_fields = fields


class ProductSerializer(serializers.ModelSerializer):
    categoria = serializers.PrimaryKeyRelatedField(
        source="category",
        read_only=True,
    )
    nombre = serializers.CharField(source="name", read_only=True)
    descripcion = serializers.CharField(source="description", read_only=True)
    precio = serializers.DecimalField(
        source="price",
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )
    activo = serializers.BooleanField(source="active", read_only=True)
    creado_en = serializers.DateTimeField(source="created_at", read_only=True)
    actualizado_en = serializers.DateTimeField(source="updated_at", read_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "categoria",
            "nombre",
            "slug",
            "descripcion",
            "precio",
            "stock",
            "activo",
            "creado_en",
            "actualizado_en",
        )
        read_only_fields = fields
