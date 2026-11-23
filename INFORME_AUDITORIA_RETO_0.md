# 5. Informe de auditoría del reto 0

Diligenciado durante las actividades 2 y 3. Toda evidencia cita el archivo y la línea del código donde se encuentra.

---

## 5.1 Datos del prototipo

| Campo | Respuesta |
| :--- | :--- |
| **Aprendiz** | Ivan Andres Diaz Lizcano |
| **Enunciado asignado (número y nombre)** | 10. Acortador de enlaces |
| **Herramienta y modelo de IA utilizados** | GitHub Copilot (GPT-4o) |
| **Tiempo empleado** | 18 minutos |
| **¿La aplicación arrancó? (Sí / No)** | Sí |
| **Cantidad de correcciones pedidas a la IA** | 0 |

---

## 5.2 Prompt utilizado

```text
Crea una aplicación web en Python para acortar enlaces y contar las visitas de cada uno, con inicio de sesión.
```

---

## 5.3 Lista de verificación

| Criterio | Pregunta de verificación | Resultado | Evidencia (archivo y línea) |
| :--- | :--- | :---: | :--- |
| **Ejecución** | ¿La aplicación arranca siguiendo solo las instrucciones disponibles? | **Cumple** | [README.md](file:///C:/Users/Aprendiz/vibecoding3/README.md#L8-L23), [requirements.txt](file:///C:/Users/Aprendiz/vibecoding3/requirements.txt#L1) y [app.py](file:///C:/Users/Aprendiz/vibecoding3/app.py#L129-L131). |
| **Validación de entradas** | ¿Rechaza campos vacíos, textos extensos y caracteres especiales? | **No cumple** | [app.py](file:///C:/Users/Aprendiz/vibecoding3/app.py#L46-L47) y [app.py](file:///C:/Users/Aprendiz/vibecoding3/app.py#L89-L93). No valida longitud, URLs inválidas (`javascript:`) ni caracteres HTML. |
| **Contraseñas y hash** | ¿Las contraseñas se guardan con una función de hash y no en texto plano? | **No cumple** | [app.py](file:///C:/Users/Aprendiz/vibecoding3/app.py#L50) y [app.py](file:///C:/Users/Aprendiz/vibecoding3/app.py#L65). Se guardan y comparan directamente en texto plano. |
| **Secretos y claves** | ¿Hay claves o credenciales escritas directamente en el código? | **No cumple** | [app.py](file:///C:/Users/Aprendiz/vibecoding3/app.py#L7). `app.secret_key = "super_secret_vibe_coding_key_12345"` hardcodeada en texto claro. |
| **Control de acceso** | ¿Un usuario puede ver o modificar los datos de otro usuario? | **No cumple** | [app.py](file:///C:/Users/Aprendiz/vibecoding3/app.py#L122-L126). La ruta `/eliminar/<id>` elimina por ID sin verificar si pertenece al `session['user_id']` (vulnerabilidad IDOR). |
| **Dependencias y alucinación** | ¿Cada paquete existe en pypi.org, es necesario y está vigente? | **Cumple** | [requirements.txt](file:///C:/Users/Aprendiz/vibecoding3/requirements.txt#L1). El paquete `Flask==3.0.3` existe en pypi.org y es el estándar esperado. |
| **Pruebas** | ¿Existen pruebas automatizadas? ¿Cuántas pasan? | **No cumple** | No se generaron archivos de prueba (`test_*.py`) ni configuración para pytest. |
| **Manejo de errores** | ¿Los errores muestran mensajes claros, sin exponer detalles internos? | **Parcial** | [app.py](file:///C:/Users/Aprendiz/vibecoding3/app.py#L131). Ejecuta con `debug=True`, exponiendo la consola interactiva de depuración y stack traces. |
| **Estructura** | ¿El código está organizado en partes o todo está en un solo archivo? | **No cumple** | [app.py](file:///C:/Users/Aprendiz/vibecoding3/app.py#L1-L132). Toda la lógica, modelos, consultas SQL y rutas están unificadas en un único archivo monolítico. |

---

## 5.4 Fallos y decisiones relevantes

Describa al menos tres fallos o decisiones cuestionables que encontró en el código generado:

| N.º | Descripción del fallo | Archivo y línea | Riesgo para el usuario o el cliente | Corrección propuesta |
| :---: | :--- | :--- | :--- | :--- |
| **1** | **Contraseñas almacenadas en texto plano** sin aplicar función hash criptográfica. | [app.py](file:///C:/Users/Aprendiz/vibecoding3/app.py#L50) y [app.py](file:///C:/Users/Aprendiz/vibecoding3/app.py#L65) | Si la base de datos SQLite se filtra, se descarga o se expone indebidamente, todas las contraseñas quedan al descubierto inmediatamente, comprometiendo la seguridad de los usuarios. | Utilizar algoritmos estándar de derivación de claves como `werkzeug.security` (`generate_password_hash` / `check_password_hash`) o `bcrypt` antes de insertar el registro en la base de datos. |
| **2** | **Clave secreta (`SECRET_KEY`) hardcodeada** directamente en el código fuente. | [app.py](file:///C:/Users/Aprendiz/vibecoding3/app.py#L7) | Cualquier persona con acceso de lectura al repositorio de código puede firmar y falsificar cookies de sesión (`session cookie tampering`), suplantando la identidad de cualquier usuario. | Cargar la clave desde variables de entorno (`os.environ.get("SECRET_KEY")`) usando un archivo `.env` que se mantenga fuera del control de versiones. |
| **3** | **Falla de control de acceso a nivel de objeto (IDOR / BOLA)** en la eliminación de enlaces. | [app.py](file:///C:/Users/Aprendiz/vibecoding3/app.py#L122-L126) | Un usuario con sesión iniciada puede borrar los enlaces acortados de cualquier otro usuario simplemente cambiando el número de ID en la URL `/eliminar/<id>`. | Restringir la consulta SQL para que siempre verifique la pertenencia al usuario en sesión: `DELETE FROM urls WHERE id = ? AND user_id = ?`. |
| **4** | **Ausencia de validación y sanitización de URLs**. | [app.py](file:///C:/Users/Aprendiz/vibecoding3/app.py#L89-L93) | Permite registrar enlaces con protocolos inseguros o maliciosos (por ejemplo `javascript:...`), campos en blanco o inyecciones que alteran la presentación visual. | Validar esquemas HTTP/HTTPS permitidos con `urllib.parse` y sanitizar los campos contra ataques XSS antes de almacenarlos. |

---

## 5.5 Conclusiones

1. **¿La aplicación podría entregarse a un cliente? Justifique su respuesta con base en los hallazgos de la auditoría, en máximo cinco líneas.**  
   *No, de ninguna manera. El prototipo presenta fallos críticos de seguridad como el almacenamiento de contraseñas en texto plano, exposición de claves criptográficas en el código y vulnerabilidad IDOR que permite borrar datos de otros usuarios. Entregar este software expondría al cliente a fugas de información, suplantación de identidad y responsabilidades legales severas.*

2. **¿Qué información le faltó al prompt para evitar los fallos que encontró? Mencione al menos dos requisitos que debieron declararse de forma explícita.**  
   *Al prompt le faltó: 1) Exigir explícitamente buenas prácticas de seguridad: "Almacenar contraseñas mediante hashing seguro (bcrypt o argon2), separar la configuración sensible en variables de entorno y validar la autorización de cada usuario sobre sus propios recursos", y 2) Requerir validaciones de entrada robustas y arquitectura modular: "Sanitizar URLs evitando esquemas peligrosos y separar la aplicación en controladores, modelos y rutas con pruebas automatizadas".*
