import os
from uuid import uuid4


def _unique_suffix() -> str:
    worker = os.getenv("PYTEST_XDIST_WORKER", "local").replace("-", "")
    return f"{worker}{uuid4().hex[:12]}"


def build_user_data() -> dict[str, str]:
    suffix = _unique_suffix()
    return {
        "usuario": f"qa_{suffix}",
        "correo": f"qa_{suffix}@example.test",
        "contrasena": f"Api!2026-{uuid4().hex}",
        "confirmacion_contrasena": "",
    }


def build_complete_user_data() -> dict[str, str]:
    user_data = build_user_data()
    user_data["confirmacion_contrasena"] = user_data["contrasena"]
    return user_data


def build_delivery_data() -> dict[str, str]:
    suffix = _unique_suffix()
    return {
        "nombre_destinatario": "Cliente Automatización",
        "direccion": f"Calle de Pruebas {suffix}",
        "ciudad": "Madrid",
        "codigo_postal": "28001",
        "pais": "España",
    }
