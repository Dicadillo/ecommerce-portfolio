from django.test import Client


def test_endpoint_de_salud_devuelve_estado_correcto():
    cliente = Client()

    respuesta = cliente.get("/api/salud/")

    assert respuesta.status_code == 200
    assert respuesta.headers["Content-Type"] == "application/json"
    assert respuesta.json() == {"status": "ok"}


def test_endpoint_de_salud_es_publico_incluso_con_token_invalido():
    cliente = Client(HTTP_AUTHORIZATION="Bearer token-no-valido")

    respuesta = cliente.get("/api/salud/")

    assert respuesta.status_code == 200
    assert respuesta.json() == {"status": "ok"}
