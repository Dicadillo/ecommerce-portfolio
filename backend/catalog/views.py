from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    extend_schema,
    extend_schema_view,
)
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ReadOnlyModelViewSet

from catalog.filters import (
    CatalogOrderingFilter,
    CatalogSearchFilter,
    ProductFilterBackend,
)
from catalog.models import Category, Product
from catalog.pagination import CatalogPagination
from catalog.serializers import CategorySerializer, ProductSerializer
from config.openapi import BAD_REQUEST_RESPONSE, NOT_FOUND_RESPONSE


@extend_schema_view(
    list=extend_schema(
        tags=["Catálogo"],
        summary="Listar categorías",
        description="Devuelve las categorías del catálogo de forma paginada.",
        auth=[],
        examples=[
            OpenApiExample(
                "Listado de categorías",
                value={
                    "conteo": 1,
                    "siguiente": None,
                    "anterior": None,
                    "resultados": [
                        {
                            "id": 1,
                            "nombre": "Portátiles",
                            "slug": "portatiles",
                            "activo": True,
                            "creado_en": "2026-01-15T10:00:00Z",
                            "actualizado_en": "2026-01-15T10:00:00Z",
                        }
                    ],
                },
                response_only=True,
            )
        ],
    ),
    retrieve=extend_schema(
        tags=["Catálogo"],
        summary="Consultar una categoría",
        description="Devuelve una categoría por su identificador.",
        auth=[],
        responses={200: CategorySerializer, 404: NOT_FOUND_RESPONSE},
        examples=[
            OpenApiExample(
                "Categoría",
                value={
                    "id": 1,
                    "nombre": "Portátiles",
                    "slug": "portatiles",
                    "activo": True,
                    "creado_en": "2026-01-15T10:00:00Z",
                    "actualizado_en": "2026-01-15T10:00:00Z",
                },
                response_only=True,
            )
        ],
    ),
)
class CategoryViewSet(ReadOnlyModelViewSet):
    authentication_classes = ()
    permission_classes = (AllowAny,)
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = CatalogPagination


@extend_schema_view(
    list=extend_schema(
        tags=["Catálogo"],
        summary="Listar productos",
        description=(
            "Devuelve los productos de forma paginada. Permite filtrar, buscar "
            "por nombre y ordenar por nombre o precio."
        ),
        auth=[],
        parameters=[
            OpenApiParameter(
                "categoria",
                OpenApiTypes.INT,
                description="Identificador de la categoría.",
            ),
            OpenApiParameter(
                "activo",
                OpenApiTypes.BOOL,
                description="Filtra por estado activo.",
            ),
            OpenApiParameter(
                "con_stock",
                OpenApiTypes.BOOL,
                description="Filtra productos con o sin unidades disponibles.",
            ),
            OpenApiParameter(
                "buscar",
                OpenApiTypes.STR,
                description="Texto incluido en el nombre del producto.",
            ),
            OpenApiParameter(
                "ordenar",
                OpenApiTypes.STR,
                enum=["nombre", "-nombre", "precio", "-precio"],
                description="Campo y sentido de ordenación.",
            ),
        ],
        responses={200: ProductSerializer(many=True), 400: BAD_REQUEST_RESPONSE},
        examples=[
            OpenApiExample(
                "Listado de productos",
                value={
                    "conteo": 1,
                    "siguiente": None,
                    "anterior": None,
                    "resultados": [
                        {
                            "id": 10,
                            "categoria": 1,
                            "nombre": "Portátil QA",
                            "slug": "portatil-qa",
                            "descripcion": "Equipo para automatización.",
                            "precio": "1299.90",
                            "stock": 8,
                            "activo": True,
                            "creado_en": "2026-01-15T10:00:00Z",
                            "actualizado_en": "2026-01-15T10:00:00Z",
                        }
                    ],
                },
                response_only=True,
            )
        ],
    ),
    retrieve=extend_schema(
        tags=["Catálogo"],
        summary="Consultar un producto",
        description="Devuelve un producto por su identificador.",
        auth=[],
        responses={200: ProductSerializer, 404: NOT_FOUND_RESPONSE},
        examples=[
            OpenApiExample(
                "Producto",
                value={
                    "id": 10,
                    "categoria": 1,
                    "nombre": "Portátil QA",
                    "slug": "portatil-qa",
                    "descripcion": "Equipo para automatización.",
                    "precio": "1299.90",
                    "stock": 8,
                    "activo": True,
                    "creado_en": "2026-01-15T10:00:00Z",
                    "actualizado_en": "2026-01-15T10:00:00Z",
                },
                response_only=True,
            )
        ],
    ),
)
class ProductViewSet(ReadOnlyModelViewSet):
    authentication_classes = ()
    permission_classes = (AllowAny,)
    queryset = Product.objects.select_related("category").all()
    serializer_class = ProductSerializer
    pagination_class = CatalogPagination
    filter_backends = (
        ProductFilterBackend,
        CatalogSearchFilter,
        CatalogOrderingFilter,
    )
    search_fields = ("name",)
