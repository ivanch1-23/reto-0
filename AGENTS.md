# AGENTS.md

## Proyecto
Aplicación web en Python con Flask para acortar enlaces y registrar estadísticas de visitas por URL.
Cuenta con sistema de autenticación de usuarios y panel de administración de enlaces personales.

## Stack
- Python 3.13 / Flask 3.0.3 / Jinja2 / SQLite3 / python-dotenv
- Pruebas con pytest y análisis estático con Ruff

## Comandos
- Instalar dependencias: pip install -r requirements.txt
- Ejecutar aplicación: python app.py
- Pruebas automatizadas: python -m pytest -v
- Revisar estilo y calidad: ruff check .

## Estructura
- app.py: Rutas web, lógica de acortamiento, base de datos y autenticación
- requirements.txt: Dependencias del proyecto
- .env.example: Plantilla de variables de entorno requeridas
- templates/: Plantillas HTML con Jinja2 (base, login, register, dashboard)
- tests/: Pruebas automatizadas (humo y regresión de fallos)

## Qué no hacer
- No modificar las pruebas existentes para que pasen.
- No escribir claves ni secretos directamente en el código fuente.
- No instalar dependencias adicionales sin explicar su justificación técnica.
- No hacer commit ni push: los ejecuta el desarrollador desde la terminal.

## Lecciones aprendidas
- Las contraseñas se guardan siempre con función de hash (werkzeug.security), nunca en texto plano.
- Antes de modificar o eliminar un registro, verificar siempre que pertenece al usuario en sesión.
- Validar en el servidor que los campos obligatorios no estén vacíos, respeten límites y bloqueen esquemas maliciosos.
