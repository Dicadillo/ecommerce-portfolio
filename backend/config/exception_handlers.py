from rest_framework.views import exception_handler


def api_exception_handler(exception, context):
    response = exception_handler(exception, context)
    if response is not None and isinstance(response.data, dict):
        detail = response.data.pop("detail", None)
        if detail is not None:
            response.data["detalle"] = detail
    return response
