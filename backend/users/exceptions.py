from rest_framework.exceptions import APIException


class InvalidCredentials(APIException):
    status_code = 401
    default_detail = {"detalle": "Las credenciales son incorrectas."}
    default_code = "invalid_credentials"
