import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError

from catalog.models import Category, Product

DEMO_PASSWORD = "PortfolioDemo!9842"


@pytest.mark.django_db
def test_demo_data_command_is_idempotent(monkeypatch, capsys):
    monkeypatch.setenv("USUARIO_DEMO_CONTRASENA", DEMO_PASSWORD)

    call_command("cargar_datos_demo")
    call_command("cargar_datos_demo")

    user = get_user_model().objects.get(username="cliente_demo")
    output = capsys.readouterr().out
    assert Category.objects.count() == 4
    assert Product.objects.count() == 12
    assert Product.objects.filter(stock=0).exists()
    assert Product.objects.filter(stock__gt=0).exists()
    assert Product.objects.filter(active=False).exists()
    assert Product.objects.filter(active=True).exists()
    assert get_user_model().objects.filter(username="cliente_demo").count() == 1
    assert user.check_password(DEMO_PASSWORD)
    assert DEMO_PASSWORD not in output


@pytest.mark.django_db
def test_demo_data_command_requires_password(monkeypatch):
    monkeypatch.delenv("USUARIO_DEMO_CONTRASENA", raising=False)

    with pytest.raises(CommandError, match="USUARIO_DEMO_CONTRASENA"):
        call_command("cargar_datos_demo")

    assert not Category.objects.exists()
    assert not Product.objects.exists()


@pytest.mark.django_db
def test_demo_data_command_rejects_weak_password(monkeypatch):
    monkeypatch.setenv("USUARIO_DEMO_CONTRASENA", "123")

    with pytest.raises(CommandError, match="no supera los validadores"):
        call_command("cargar_datos_demo")

    assert not Category.objects.exists()
    assert not Product.objects.exists()
