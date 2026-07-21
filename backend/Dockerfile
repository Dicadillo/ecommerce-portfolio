# syntax=docker/dockerfile:1.7

FROM ghcr.io/astral-sh/uv:0.11.29 AS uv

FROM python:3.13-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH="/opt/venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=config.settings_production

COPY --from=uv /uv /uvx /usr/local/bin/

RUN groupadd --gid 10001 django \
    && useradd --uid 10001 --gid django --create-home --shell /usr/sbin/nologin django

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

COPY --chown=django:django manage.py ./
COPY --chown=django:django cart/ cart/
COPY --chown=django:django catalog/ catalog/
COPY --chown=django:django config/ config/
COPY --chown=django:django orders/ orders/
COPY --chown=django:django payments/ payments/
COPY --chown=django:django salud/ salud/
COPY --chown=django:django users/ users/
COPY --chown=django:django --chmod=755 docker/entrypoint.sh /usr/local/bin/backend-entrypoint

RUN mkdir -p /app/staticfiles \
    && chown django:django /app/staticfiles

USER django

EXPOSE 8000

ENTRYPOINT ["backend-entrypoint"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "60", "--access-logfile", "-", "--error-logfile", "-"]
