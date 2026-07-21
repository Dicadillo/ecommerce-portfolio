# Despliegue seguro del backend

El desarrollo usa `config.settings`. Un despliegue debe definir
`DJANGO_SETTINGS_MODULE=config.settings_production` y proporcionar todas las
credenciales mediante variables de entorno o un gestor de secretos.

La configuración de producción exige una clave secreta y una lista explícita de
hosts, fuerza HTTPS, activa HSTS y marca como seguras las cookies de sesión y
CSRF. También mantiene `DEBUG=False` y configura conexiones persistentes a la
base de datos. Producción exige PostgreSQL y no permite el fallback SQLite de
desarrollo.

Variables específicas de producción:

- `DJANGO_CLAVE_SECRETA`: valor largo, aleatorio y no compartido con JWT si se
  define `JWT_CLAVE_FIRMA`.
- `DJANGO_HOSTS_PERMITIDOS`: hosts separados por comas, sin comodines amplios.
- `DJANGO_ORIGENES_CSRF`: orígenes HTTPS autorizados para Django Admin.
- `DJANGO_REDIRECCION_HTTPS`: debe permanecer activo tras verificar el proxy.
- `DJANGO_CONFIAR_PROXY_HTTPS`: activar solo si el proxy controla y reemplaza
  `X-Forwarded-Proto`.
- `DJANGO_HSTS_SEGUNDOS`: se recomienda un año después de validar HTTPS.
- `POSTGRES_TIEMPO_CONEXION`: reutilización de conexiones en segundos.

La API utiliza JWT en la cabecera `Authorization`, no cookies de autenticación.
El middleware CSRF se mantiene para Django Admin. CORS no está habilitado, por lo
que los navegadores no pueden consumir la API desde otros orígenes. Cuando exista
un frontend con origen distinto se debe añadir una lista cerrada de orígenes; no
se debe permitir `*` junto con credenciales.

Antes de desplegar:

```bash
DJANGO_SETTINGS_MODULE=config.settings_production \
DJANGO_CLAVE_SECRETA='<valor-seguro>' \
DJANGO_HOSTS_PERMITIDOS='api.example.com' \
uv run python manage.py check --deploy
```

Los archivos `.env`, variantes `.env.*`, claves privadas, certificados y
resultados de cobertura están excluidos de Git. Los archivos `.env.example` solo
contienen marcadores y sí se versionan.
