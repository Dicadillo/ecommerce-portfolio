# E-commerce QA Automation Portfolio

Monorepo para un portfolio profesional de QA Automation/SDET. El backend está
construido con Django REST Framework, PostgreSQL y JWT; incluye catálogo,
carrito, pedidos, pagos simulados y documentación OpenAPI. Las suites externas
se organizan en `automation`. El frontend usa React, TypeScript y Vite como base
para consumir la API REST.

## Arquitectura

- `backend`: API Django, tests y contenedor de producción con Gunicorn.
- `frontend`: cliente React con enrutado, cliente HTTP y pruebas unitarias.
- `automation`: suites API, Playwright, Selenium y Robot Framework.
- `infrastructure`: recursos adicionales de infraestructura y CI/CD.
- `docs`: decisiones de arquitectura, seguridad y despliegue.
- `compose.yml`: PostgreSQL persistente y backend ejecutable localmente.

## Variables de entorno

Copia el archivo de ejemplo y sustituye todos los marcadores antes de levantar
los servicios:

```bash
cp .env.example .env
```

Variables requeridas:

- `DJANGO_CLAVE_SECRETA`: clave larga y aleatoria de Django.
- `JWT_CLAVE_FIRMA`: clave independiente para firmar JWT.
- `DJANGO_HOSTS_PERMITIDOS`: hosts separados por comas.
- `POSTGRES_DB`: nombre de la base de datos.
- `POSTGRES_USER`: usuario de PostgreSQL.
- `POSTGRES_PASSWORD`: contraseña local de PostgreSQL.

Variables operativas opcionales:

- `POSTGRES_PORT`: puerto publicado de PostgreSQL; por defecto `5432`.
- `BACKEND_PORT`: puerto publicado de la API; por defecto `8000`.
- `DJANGO_EJECUTAR_MIGRACIONES`: controla las migraciones del entrypoint.
- `DJANGO_RECOLECTAR_ESTATICOS`: controla `collectstatic` en el entrypoint.
- `USUARIO_DEMO_CONTRASENA`: obligatoria únicamente al cargar datos demo.
- `USUARIO_DEMO_NOMBRE` y `USUARIO_DEMO_CORREO`: personalizan el cliente demo.

El Compose local desactiva la redirección HTTPS para permitir peticiones en
`localhost` y marca las cookies como no seguras únicamente para que Django Admin
funcione sobre HTTP local. En un despliegue real deben mantenerse HTTPS y las
cookies seguras siguiendo la guía
[docs/backend-deployment.md](docs/backend-deployment.md).

## Levantar y detener el entorno

Construir y levantar PostgreSQL y el backend:

```bash
docker compose up --build -d
docker compose ps
```

El backend espera a que PostgreSQL esté disponible, aplica migraciones,
recopila estáticos y arranca Gunicorn. Para detener los servicios conservando el
volumen de datos:

```bash
docker compose down
```

Ver logs:

```bash
docker compose logs -f backend
docker compose logs -f db
```

## Migraciones

Las migraciones se ejecutan automáticamente en el único contenedor backend del
Compose. También pueden ejecutarse manualmente:

```bash
docker compose exec backend python manage.py migrate --noinput
```

Con varias réplicas, desactiva `DJANGO_EJECUTAR_MIGRACIONES` y ejecuta las
migraciones como una tarea única antes de desplegar la nueva versión.

## Datos demo

Los datos semilla son exclusivamente para desarrollo y demostraciones. No deben
cargarse en producción. El comando es idempotente y requiere que la contraseña
se proporcione explícitamente:

```bash
docker compose exec \
  -e USUARIO_DEMO_CONTRASENA='<contrasena-demo-local>' \
  backend python manage.py cargar_datos_demo
```

Crea cuatro categorías, doce productos con combinaciones de stock y actividad,
y el usuario cliente `cliente_demo`. No crea un administrador.

## Tests y controles de calidad

La imagen final contiene únicamente dependencias de producción. Los tests se
ejecutan fuera del contenedor:

```bash
cd backend
uv sync
uv run python manage.py check
uv run pytest
uv run pytest --cov --cov-report=term-missing
uv run ruff check .
uv run ruff format --check .
```

## Desarrollo del frontend

La configuración pública de la API se copia desde el ejemplo local. Las
variables con prefijo `VITE_` se incorporan al código servido al navegador, por
lo que nunca deben contener secretos:

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

Por defecto, el cliente utiliza `VITE_API_URL=http://127.0.0.1:8000/api/`. La
aplicación de desarrollo queda disponible en <http://127.0.0.1:5173/>.

Controles disponibles:

```bash
npm run lint
npm run test
npm run test:watch
npm run build
npm run preview
npm run format:check
```

## URLs locales

- API y comprobación de salud: <http://127.0.0.1:8000/api/salud/>
- Catálogo: <http://127.0.0.1:8000/api/productos/>
- Esquema OpenAPI: <http://127.0.0.1:8000/api/esquema/>
- Swagger UI: <http://127.0.0.1:8000/api/documentacion/>
- ReDoc: <http://127.0.0.1:8000/api/redoc/>
- Django Admin: <http://127.0.0.1:8000/admin/>
