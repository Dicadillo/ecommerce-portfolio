from config.exceptions import AuthenticationError


class InvalidCredentials(AuthenticationError):
    default_detail = "Las credenciales son incorrectas."
    default_code = "credenciales_invalidas"
