#!/bin/sh
set -eu

is_enabled() {
    case "${1:-}" in
        1|true|True|yes|Yes|si|sí|Si|Sí) return 0 ;;
        *) return 1 ;;
    esac
}

max_attempts="${POSTGRES_INTENTOS_CONEXION:-30}"
attempt=1

echo "Esperando a PostgreSQL..."
until python -c "import django; django.setup(); from django.db import connection; connection.ensure_connection()" >/dev/null 2>&1; do
    if [ "$attempt" -ge "$max_attempts" ]; then
        echo "No se pudo conectar a PostgreSQL tras ${max_attempts} intentos." >&2
        exit 1
    fi
    echo "PostgreSQL todavía no está disponible (${attempt}/${max_attempts})."
    attempt=$((attempt + 1))
    sleep 2
done
echo "PostgreSQL disponible."

if is_enabled "${DJANGO_EJECUTAR_MIGRACIONES:-true}"; then
    echo "Aplicando migraciones..."
    python manage.py migrate --noinput
fi

if is_enabled "${DJANGO_RECOLECTAR_ESTATICOS:-true}"; then
    echo "Recopilando archivos estáticos..."
    python manage.py collectstatic --noinput --clear
fi

exec "$@"
