*** Settings ***
Documentation       Pruebas de regresión del carrito.
Resource            ../../resources/common.resource
Resource            ../../resources/auth.resource
Resource            ../../resources/cart.resource

Suite Setup         Abrir Ecommerce
Suite Teardown      Cerrar Ecommerce

Test Tags           regression    cart

*** Test Cases ***
El Usuario Puede Añadir Un Producto Al Carrito
    [Documentation]    Pendiente de implementar.
    Skip    Caso pendiente de implementar