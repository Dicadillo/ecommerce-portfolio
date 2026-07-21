import os
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from catalog.models import Category, Product

DEMO_CATEGORIES = (
    {"name": "Electrónica", "slug": "electronica", "active": True},
    {"name": "Libros", "slug": "libros", "active": True},
    {"name": "Hogar", "slug": "hogar", "active": True},
    {"name": "Laboratorio QA", "slug": "laboratorio-qa", "active": True},
)

DEMO_PRODUCTS = (
    {
        "category": "electronica",
        "name": "Portátil Automation Pro",
        "slug": "portatil-automation-pro",
        "description": "Equipo de demostración para ejecutar suites automatizadas.",
        "price": Decimal("1299.90"),
        "stock": 8,
        "active": True,
    },
    {
        "category": "electronica",
        "name": "Monitor Ultrawide QA",
        "slug": "monitor-ultrawide-qa",
        "description": "Monitor panorámico para entornos de pruebas.",
        "price": Decimal("449.50"),
        "stock": 0,
        "active": True,
    },
    {
        "category": "electronica",
        "name": "Teclado Mecánico SDET",
        "slug": "teclado-mecanico-sdet",
        "description": "Teclado mecánico de demostración.",
        "price": Decimal("89.99"),
        "stock": 15,
        "active": True,
    },
    {
        "category": "electronica",
        "name": "Ratón Legacy",
        "slug": "raton-legacy",
        "description": "Producto inactivo para escenarios negativos.",
        "price": Decimal("24.95"),
        "stock": 4,
        "active": False,
    },
    {
        "category": "libros",
        "name": "Automatización de APIs",
        "slug": "automatizacion-de-apis",
        "description": "Guía práctica para pruebas automatizadas de APIs.",
        "price": Decimal("34.90"),
        "stock": 20,
        "active": True,
    },
    {
        "category": "libros",
        "name": "Patrones para Playwright",
        "slug": "patrones-para-playwright",
        "description": "Patrones mantenibles para automatización web.",
        "price": Decimal("39.50"),
        "stock": 7,
        "active": True,
    },
    {
        "category": "libros",
        "name": "Selenium Clásico",
        "slug": "selenium-clasico",
        "description": "Edición retirada para validar productos inactivos.",
        "price": Decimal("19.90"),
        "stock": 0,
        "active": False,
    },
    {
        "category": "hogar",
        "name": "Lámpara de Escritorio",
        "slug": "lampara-de-escritorio",
        "description": "Iluminación regulable para el espacio de trabajo.",
        "price": Decimal("45.00"),
        "stock": 12,
        "active": True,
    },
    {
        "category": "hogar",
        "name": "Soporte para Portátil",
        "slug": "soporte-para-portatil",
        "description": "Soporte ergonómico de aluminio.",
        "price": Decimal("32.75"),
        "stock": 0,
        "active": True,
    },
    {
        "category": "laboratorio-qa",
        "name": "Licencia de Pruebas Simulada",
        "slug": "licencia-de-pruebas-simulada",
        "description": "Producto ficticio para escenarios de checkout.",
        "price": Decimal("99.00"),
        "stock": 50,
        "active": True,
    },
    {
        "category": "laboratorio-qa",
        "name": "Dispositivo Móvil de Pruebas",
        "slug": "dispositivo-movil-de-pruebas",
        "description": "Terminal ficticio para automatización móvil.",
        "price": Decimal("299.00"),
        "stock": 3,
        "active": True,
    },
    {
        "category": "laboratorio-qa",
        "name": "Nodo de Ejecución Agotado",
        "slug": "nodo-de-ejecucion-agotado",
        "description": "Producto sin stock para pruebas de validación.",
        "price": Decimal("159.00"),
        "stock": 0,
        "active": True,
    },
)


class Command(BaseCommand):
    help = "Carga datos reproducibles para desarrollo y demostraciones."

    def handle(self, *args, **options):
        password = os.environ.get("USUARIO_DEMO_CONTRASENA")
        if not password:
            raise CommandError(
                "Define USUARIO_DEMO_CONTRASENA para crear el usuario demo."
            )

        username = os.environ.get("USUARIO_DEMO_NOMBRE", "cliente_demo")
        email = os.environ.get(
            "USUARIO_DEMO_CORREO",
            "cliente.demo@example.com",
        )

        with transaction.atomic():
            categories = self._load_categories()
            self._load_products(categories)
            user, created = self._load_user(username, email, password)

        user_state = "creado" if created else "actualizado"
        self.stdout.write(
            self.style.SUCCESS(
                f"Datos demo cargados: {len(categories)} categorías, "
                f"{len(DEMO_PRODUCTS)} productos y usuario {user_state}."
            )
        )

    def _load_categories(self):
        categories = {}
        for values in DEMO_CATEGORIES:
            category, _ = Category.objects.update_or_create(
                slug=values["slug"],
                defaults={
                    "name": values["name"],
                    "active": values["active"],
                },
            )
            categories[category.slug] = category
        return categories

    def _load_products(self, categories):
        for values in DEMO_PRODUCTS:
            Product.objects.update_or_create(
                slug=values["slug"],
                defaults={
                    "category": categories[values["category"]],
                    "name": values["name"],
                    "description": values["description"],
                    "price": values["price"],
                    "stock": values["stock"],
                    "active": values["active"],
                },
            )

    def _load_user(self, username, email, password):
        user_model = get_user_model()
        user, created = user_model.objects.get_or_create(
            username=username,
            defaults={"email": email},
        )
        user.email = email
        try:
            validate_password(password, user=user)
        except DjangoValidationError as error:
            raise CommandError(
                "La contraseña demo no supera los validadores."
            ) from error
        if not user.check_password(password):
            user.set_password(password)
        user.save(update_fields=("email", "password"))
        return user, created
