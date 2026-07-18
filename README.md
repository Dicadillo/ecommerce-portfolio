# E-commerce QA Automation Portfolio

Monorepo para un portfolio profesional de QA Automation/SDET basado en una
aplicación de e-commerce.

La arquitectura separa la aplicación en `backend` y `frontend`, y agrupa las
suites de pruebas externas en `automation`: API con pytest/httpx, UI con
Playwright, una suite adicional con Selenium y pruebas con Robot Framework.
`infrastructure` contendrá la configuración de contenedores y CI/CD, mientras
que `docs` reunirá la arquitectura y la estrategia de pruebas.

En esta fase solo se define la estructura inicial. Django, React y sus
dependencias se incorporarán en incrementos posteriores.
