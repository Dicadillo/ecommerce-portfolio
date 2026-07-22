import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class ApiSettings:
    base_url: str
    timeout_seconds: float


def load_settings() -> ApiSettings:
    project_directory = Path(__file__).resolve().parents[1]
    load_dotenv(project_directory / ".env")

    base_url = os.getenv("API_BASE_URL", "http://127.0.0.1:8000/api/")
    timeout_value = os.getenv("API_TIMEOUT_SECONDS", "10")

    try:
        timeout_seconds = float(timeout_value)
    except ValueError as error:
        raise ValueError("API_TIMEOUT_SECONDS debe ser un número.") from error
    if timeout_seconds <= 0:
        raise ValueError("API_TIMEOUT_SECONDS debe ser mayor que cero.")

    return ApiSettings(
        base_url=base_url.rstrip("/") + "/",
        timeout_seconds=timeout_seconds,
    )
