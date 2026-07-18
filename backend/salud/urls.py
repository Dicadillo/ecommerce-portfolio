from django.urls import path

from salud.views import comprobar_salud

urlpatterns = [
    path("", comprobar_salud, name="comprobar-salud"),
]
