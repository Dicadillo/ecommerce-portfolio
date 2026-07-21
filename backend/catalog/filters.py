from rest_framework import filters
from rest_framework.exceptions import ValidationError


class ProductFilterBackend(filters.BaseFilterBackend):
    true_values = frozenset({"1", "true", "si", "sí"})
    false_values = frozenset({"0", "false", "no"})

    def filter_queryset(self, request, queryset, view):
        category = request.query_params.get("categoria")
        active = self._parse_boolean(request, "activo")
        in_stock = self._parse_boolean(request, "con_stock")

        if category is not None:
            try:
                category_id = int(category)
            except (TypeError, ValueError) as error:
                raise ValidationError(
                    {"categoria": "Debe ser un identificador entero."}
                ) from error

            if category_id < 1:
                raise ValidationError(
                    {"categoria": "Debe ser un identificador entero positivo."}
                )
            queryset = queryset.filter(category_id=category_id)

        if active is not None:
            queryset = queryset.filter(active=active)

        if in_stock is True:
            queryset = queryset.filter(stock__gt=0)
        elif in_stock is False:
            queryset = queryset.filter(stock=0)

        return queryset

    def _parse_boolean(self, request, parameter):
        value = request.query_params.get(parameter)
        if value is None:
            return None

        normalized_value = value.strip().lower()
        if normalized_value in self.true_values:
            return True
        if normalized_value in self.false_values:
            return False

        raise ValidationError({parameter: "Debe ser true, false, 1, 0, sí o no."})


class CatalogSearchFilter(filters.SearchFilter):
    search_param = "buscar"


class CatalogOrderingFilter(filters.BaseFilterBackend):
    ordering_param = "ordenar"
    field_mapping = {
        "nombre": "name",
        "precio": "price",
    }

    def filter_queryset(self, request, queryset, view):
        ordering = self.get_ordering(request)
        if ordering:
            return queryset.order_by(*ordering)
        return queryset

    def get_ordering(self, request):
        requested_fields = request.query_params.get(self.ordering_param)
        if not requested_fields:
            return []

        ordering = []
        for requested_field in requested_fields.split(","):
            requested_field = requested_field.strip()
            descending = requested_field.startswith("-")
            public_field = requested_field.removeprefix("-")
            internal_field = self.field_mapping.get(public_field)
            if internal_field is None:
                raise ValidationError(
                    {
                        "ordenar": (
                            "Solo se permite ordenar por nombre o precio, "
                            "con un prefijo '-' opcional."
                        )
                    }
                )
            prefix = "-" if descending else ""
            ordering.append(f"{prefix}{internal_field}")
        return ordering
