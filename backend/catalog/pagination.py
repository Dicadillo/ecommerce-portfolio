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
