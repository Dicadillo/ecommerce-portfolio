*** Settings ***
Library         SeleniumLibrary
Library         ../libraries/EcommerceLibrary.py
Variables       ../config/variables.py

*** Variables ***
${SELENIUM_SPEED}    0
${WINDOW_WIDTH}      1440
${WINDOW_HEIGHT}     900

*** Keywords ***
Abrir Ecommerce
    [Documentation]    Abre el navegador y configura la sesión.
    ${options}=    Crear Opciones Del Navegador
    Open Browser    ${BASE_URL}    ${BROWSER}    options=${options}
    Set Selenium Timeout    ${DEFAULT_TIMEOUT}
    Set Selenium Speed    ${SELENIUM_SPEED}
    Set Window Size    ${WINDOW_WIDTH}    ${WINDOW_HEIGHT}

Cerrar Ecommerce
    [Documentation]    Cierra todos los navegadores de la ejecución.
    Close All Browsers

Crear Opciones Del Navegador
    [Documentation]    Crea las opciones del navegador según el entorno.
    IF    ${HEADLESS}
        ${options}=    Evaluate
        ...    sys.modules['selenium.webdriver'].ChromeOptions()
        ...    sys, selenium.webdriver
        Call Method    ${options}    add_argument    --headless=new
        Call Method    ${options}    add_argument    --disable-gpu
        Call Method    ${options}    add_argument    --no-sandbox
    ELSE
        ${options}=    Evaluate
        ...    sys.modules['selenium.webdriver'].ChromeOptions()
        ...    sys, selenium.webdriver
    END
    RETURN    ${options}    