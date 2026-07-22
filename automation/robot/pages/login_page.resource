*** Settings ***
Library    SeleniumLibrary

*** Variables ***
${LOGIN_PATH}                 /login
${LOGIN_USERNAME_INPUT}       xpath=//input[@name="usuario"]
${LOGIN_PASSWORD_INPUT}       xpath=//input[@name="contrasena"]
${LOGIN_SUBMIT_BUTTON}        xpath=//button[@type="submit"]

*** Keywords ***
Ir A La Página De Login
    Go To    ${BASE_URL}${LOGIN_PATH}

Introducir Usuario
    [Arguments]    ${username}
    Input Text    ${LOGIN_USERNAME_INPUT}    ${username}

Introducir Contraseña
    [Arguments]    ${password}
    Input Password    ${LOGIN_PASSWORD_INPUT}    ${password}

Enviar Formulario De Login
    Click Button    ${LOGIN_SUBMIT_BUTTON}