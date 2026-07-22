*** Settings ***
Documentation       Pruebas smoke de autenticación.
Resource            ../../resources/common.resource
Resource            ../../resources/auth.resource

Suite Setup         Abrir Ecommerce
Suite Teardown      Cerrar Ecommerce

Test Tags           smoke    auth

*** Test Cases ***
El Usuario Puede Abrir La Página De Login
    [Documentation]    Comprueba que la página de autenticación es accesible.
    Ir A La Página De Login
    Location Should Be    ${BASE_URL}/login