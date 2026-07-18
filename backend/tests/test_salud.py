from django.test import Client


def test_endpoint_de_salud_devuelve_estado_correcto():
    cliente = Client()

    respuesta = cliente.get("/api/salud/")

    assert respuesta.status_code == 200
    assert respuesta.headers["Content-Type"] == "application/json"
    assert respuesta.json() == {"estado": "correcto"}
