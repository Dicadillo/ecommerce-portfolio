from rest_framework.exceptions import APIException


class BusinessRuleError(APIException):
    status_code = 400
    default_detail = "La operación incumple una regla de negocio."
    default_code = "regla_de_negocio"


class AuthenticationError(APIException):
    status_code = 401
    default_detail = "No se pudo validar la autenticación."
    default_code = "autenticacion_fallida"
