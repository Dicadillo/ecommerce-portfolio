from decimal import Decimal

from catalog.serializers import CategorySerializer, ProductSerializer


def test_category_serializer_uses_public_spanish_fields(category_factory):
    category = category_factory(name="Electrónica", slug="electronica")

    data = CategorySerializer(category).data

    assert set(data) == {
        "id",
        "nombre",
        "slug",
        "activo",
        "creado_en",
        "actualizado_en",
    }
    assert data["nombre"] == "Electrónica"
    assert "name" not in data
    assert "active" not in data


def test_product_serializer_uses_public_spanish_fields(
    product_factory,
    category_factory,
):
    category = category_factory(name="Electrónica")
    product = product_factory(
        category=category,
        name="Teclado",
        description="Teclado mecánico",
        price=Decimal("49.90"),
    )

    data = ProductSerializer(product).data

    assert set(data) == {
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
    }
    assert data["categoria"] == category.id
    assert data["nombre"] == "Teclado"
    assert data["descripcion"] == "Teclado mecánico"
    assert data["precio"] == "49.90"
    assert "name" not in data
    assert "price" not in data
