import random
import sqlite3

from app import DATABASE, app, init_db

cliente = app.test_client()


def consultar_db(query, params=(), one=False):
    conn = sqlite3.connect(DATABASE, timeout=10)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, params)
    res = cursor.fetchone() if one else cursor.fetchall()
    conn.close()
    return res


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
    fila = consultar_db("SELECT password FROM users WHERE username = ?", (usuario,), one=True)

    assert fila is not None
    # La prueba comprueba que la contraseña no se guarde en plano
    assert fila["password"] != clave_plana
    assert fila["password"].startswith(("scrypt:", "pbkdf2:", "$2b$", "$2a$"))


def test_usuario_no_puede_eliminar_enlace_de_otro():
    init_db()
    c = app.test_client()
    num1 = random.randint(10000, 99999)
    num2 = random.randint(10000, 99999)

    # 1. Registrar y loguear Usuario A
    c.post('/register', data={'username': f'user_a_{num1}', 'password': 'Password123!'}, follow_redirects=True)
    c.post('/login', data={'username': f'user_a_{num1}', 'password': 'Password123!'}, follow_redirects=True)

    # Usuario A crea un enlace
    c.post('/dashboard', data={'original_url': 'https://ejemplo.com/recurso-privado'}, follow_redirects=True)

    # Obtener el ID del enlace recién creado
    enlace_a = consultar_db(
        "SELECT id, user_id FROM urls WHERE original_url = ? ORDER BY id DESC",
        ('https://ejemplo.com/recurso-privado',),
        one=True
    )

    assert enlace_a is not None
    url_id_a = enlace_a['id']

    # 2. Cerrar sesión de A
    c.get('/logout', follow_redirects=True)

    # 3. Registrar y loguear Usuario B
    c.post('/register', data={'username': f'user_b_{num2}', 'password': 'Password123!'}, follow_redirects=True)
    c.post('/login', data={'username': f'user_b_{num2}', 'password': 'Password123!'}, follow_redirects=True)

    # Usuario B intenta eliminar el enlace de Usuario A
    respuesta = c.get(f'/eliminar/{url_id_a}', follow_redirects=False)

    # Comprobar si el enlace sigue existiendo en la base de datos
    fila_despues = consultar_db("SELECT id FROM urls WHERE id = ?", (url_id_a,), one=True)

    # El enlace NO debe haber sido eliminado y la respuesta debe ser 403 Forbidden
    assert respuesta.status_code == 403
    assert fila_despues is not None
