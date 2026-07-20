from rest_framework.viewsets import ReadOnlyModelViewSet

from catalog.filters import (
    CatalogOrderingFilter,
    CatalogSearchFilter,
    ProductFilterBackend,
)
from catalog.models import Category, Product
from catalog.pagination import CatalogPagination
from catalog.serializers import CategorySerializer, ProductSerializer


class CategoryViewSet(ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = CatalogPagination


class ProductViewSet(ReadOnlyModelViewSet):
    queryset = Product.objects.select_related("category").all()
    serializer_class = ProductSerializer
    pagination_class = CatalogPagination
    filter_backends = (
        ProductFilterBackend,
        CatalogSearchFilter,
        CatalogOrderingFilter,
    )
    search_fields = ("name",)
