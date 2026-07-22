# Automatización externa de la API

Suite independiente que prueba el ecommerce a través de HTTP, como lo haría un
consumidor real. No importa modelos, fixtures ni utilidades internas de Django.

## Requisitos

- Python 3.12 o superior.
- `uv` instalado.
- Backend y PostgreSQL disponibles mediante Docker Compose.
- Datos demo cargados, incluyendo al menos un producto activo con stock.

Desde la raíz del monorepo:

```bash
docker compose up -d --build
docker compose exec backend python manage.py cargar_datos_demo
```

## Configuración

Entra en el proyecto e instala el entorno bloqueado:

```bash
cd automation/api
uv sync
```

La configuración predeterminada apunta a `http://127.0.0.1:8000/api/`. Para
personalizarla, copia el ejemplo:

```bash
cp .env.example .env
```

Variables disponibles:

- `API_BASE_URL`: raíz de la API, con o sin barra final.
- `API_TIMEOUT_SECONDS`: tiempo máximo de cada petición HTTP.

El archivo `.env` está ignorado por Git. La suite no requiere ni contiene
usuarios, contraseñas o tokens reales.

## Ejecución

Suite completa:

```bash
uv run pytest
```

Comprobaciones críticas:

```bash
uv run pytest -m smoke
```

Cobertura funcional y casos negativos:

```bash
uv run pytest -m regression
```

Ejecución paralela:

```bash
uv run pytest -n auto
```

El modo automático está limitado a cuatro workers para proteger el backend
local y el stock compartido. Los usuarios son únicos por prueba y worker, y no
se utilizan esperas ni identificadores fijos.

Reporte HTML autocontenido:

```bash
uv run pytest --html=report.html --self-contained-html
```

Calidad estática:

```bash
uv run ruff check .
uv run ruff format --check .
```

## Estrategia de datos y limpieza

- Cada prueba crea usuarios con UUID y dominio reservado `example.test`.
- Los tokens se mantienen únicamente en memoria durante la prueba.
- El producto disponible se descubre consultando el catálogo; no se presupone
  ningún identificador.
- El carrito se vacía antes y después de los escenarios que lo utilizan.
- Los pedidos creados se cancelan o reembolsan al finalizar, devolviendo el
  stock incluso cuando falla una aserción.
- La API no ofrece borrado de usuarios, pedidos ni pagos. Estos registros de
  automatización permanecen como histórico, pero sus nombres únicos evitan
  colisiones entre ejecuciones.

## Cobertura

La suite cubre:

- salud, registro, login, refresh y perfil;
- categorías, productos, búsqueda, filtros y ordenación;
- consulta, alta, actualización, eliminación y vaciado del carrito;
- checkout, listado, detalle, aislamiento y cancelación de pedidos;
- pagos aprobados, rechazados, pendientes, duplicados y reembolsos;
- autenticación ausente o inválida, validaciones, stock insuficiente, carrito
  vacío y acceso a recursos ajenos.

El cliente registra únicamente método, ruta, estado y duración. Nunca registra
bodies, cabeceras Authorization, contraseñas, JWT, CVV ni números de tarjeta.
