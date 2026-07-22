*** Settings ***
Resource    common.resource
Resource    ../pages/login_page.resource

*** Keywords ***
Iniciar Sesión
    [Arguments]    ${username}    ${password}
    Ir A La Página De Login
    Introducir Usuario    ${username}
    Introducir Contraseña    ${password}
    Enviar Formulario De Login

Iniciar Sesión Como Usuario Demo
    Iniciar Sesión    ${DEMO_USERNAME}    ${DEMO_PASSWORD}