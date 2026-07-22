from __future__ import annotations

from robot.api.deco import keyword, library

from data.test_data import generate_unique_email, generate_unique_username


@library(scope="SUITE", auto_keywords=False)
class EcommerceLibrary:
    """Keywords auxiliares escritos en Python para la suite E2E."""

    @keyword("Generar Nombre De Usuario Único")
    def generate_username(self, prefix: str = "robot") -> str:
        return generate_unique_username(prefix)

    @keyword("Generar Correo Único")
    def generate_email(self, prefix: str = "robot") -> str:
        return generate_unique_email(prefix)

    @keyword("Obtener Últimos Cuatro Dígitos")
    def get_last_four_digits(self, card_number: str) -> str:
        cleaned_number = card_number.replace(" ", "")
        return cleaned_number[-4:]