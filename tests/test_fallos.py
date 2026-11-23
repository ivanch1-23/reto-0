import random
import sqlite3

from app import DATABASE, app, init_db

cliente = app.test_client()


def test_contrasena_se_guarda_con_hash():
    init_db()
    numero = random.randint(10000, 99999)
    usuario = f"usuario_test_{numero}"
    clave_plana = "ClaveSecreta123*"

    # Registrar usuario
    respuesta = cliente.post('/register', data={
        'username': usuario,
        'password': clave_plana
    }, follow_redirects=True)
    assert respuesta.status_code == 200

    # Consultar la contraseña guardada en la base de datos
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username = ?", (usuario,))
    fila = cursor.fetchone()
    conn.close()

    assert fila is not None
    # La prueba falla si la contraseña se guarda en texto plano
    assert fila["password"] != clave_plana
    assert fila["password"].startswith(("scrypt:", "pbkdf2:", "$2b$", "$2a$"))
