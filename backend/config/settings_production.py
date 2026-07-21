from django.core.exceptions import ImproperlyConfigured

from config.settings import *  # noqa: F403
from config.settings import BASE_DIR, DATABASES, env

DEBUG = False
SECRET_KEY = env("DJANGO_CLAVE_SECRETA")
ALLOWED_HOSTS = env.list("DJANGO_HOSTS_PERMITIDOS")
CSRF_TRUSTED_ORIGINS = env.list("DJANGO_ORIGENES_CSRF", default=[])

SECURE_SSL_REDIRECT = env.bool("DJANGO_REDIRECCION_HTTPS", default=True)
SECURE_HSTS_SECONDS = env.int("DJANGO_HSTS_SEGUNDOS", default=31536000)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

if env.bool("DJANGO_CONFIAR_PROXY_HTTPS", default=False):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

STATIC_ROOT = BASE_DIR / "staticfiles"
if DATABASES["default"]["ENGINE"] != "django.db.backends.postgresql":
    raise ImproperlyConfigured(
        "La configuración de producción requiere variables de PostgreSQL."
    )
DATABASES["default"]["CONN_MAX_AGE"] = env.int(
    "POSTGRES_TIEMPO_CONEXION",
    default=60,
)
DATABASES["default"]["CONN_HEALTH_CHECKS"] = True
