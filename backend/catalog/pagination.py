from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CatalogPagination(PageNumberPagination):
    page_size = 10
    page_query_param = "pagina"
    page_size_query_param = "tamano_pagina"
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response(
            {
                "conteo": self.page.paginator.count,
                "siguiente": self.get_next_link(),
                "anterior": self.get_previous_link(),
                "resultados": data,
            }
        )

    def get_paginated_response_schema(self, schema):
        return {
            "type": "object",
            "required": ["conteo", "resultados"],
            "properties": {
                "conteo": {"type": "integer", "example": 25},
                "siguiente": {
                    "type": "string",
                    "format": "uri",
                    "nullable": True,
                    "example": "http://localhost:8000/api/productos/?pagina=2",
                },
                "anterior": {
                    "type": "string",
                    "format": "uri",
                    "nullable": True,
                    "example": None,
                },
                "resultados": schema,
            },
        }
