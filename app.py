import os
import random
import sqlite3
import string

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, session, url_for

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "fallback-secret-key-para-desarrollo")

DATABASE = 'acortador.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            original_url TEXT,
            short_code TEXT,
            clicks INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def generar_codigo(longitud=6):
    caracteres = string.ascii_letters + string.digits
    return ''.join(random.choice(caracteres) for _ in range(longitud))

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        flash("Usuario registrado exitosamente. Inicie sesión.")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        else:
            flash("Credenciales incorrectas")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    conn = get_db()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        original_url = request.form['original_url']
        short_code = generar_codigo()
        cursor.execute(
            "INSERT INTO urls (user_id, original_url, short_code, clicks) VALUES (?, ?, ?, 0)",
            (session['user_id'], original_url, short_code)
        )
        conn.commit()
        flash(f"Enlace acortado generado: {short_code}")
        
    cursor.execute("SELECT * FROM urls WHERE user_id = ?", (session['user_id'],))
    enlaces = cursor.fetchall()
    conn.close()
    
    return render_template('dashboard.html', enlaces=enlaces, username=session.get('username'))

@app.route('/<short_code>')
def redirigir(short_code):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM urls WHERE short_code = ?", (short_code,))
    enlace = cursor.fetchone()
    
    if enlace:
        nuevo_click = enlace['clicks'] + 1
        cursor.execute("UPDATE urls SET clicks = ? WHERE id = ?", (nuevo_click, enlace['id']))
        conn.commit()
        conn.close()
        destino = enlace['original_url']
        if not destino.startswith(('http://', 'https://')):
            destino = 'http://' + destino
        return redirect(destino)
        
    conn.close()
    return "Enlace no encontrado", 404

@app.route('/eliminar/<int:url_id>')
def eliminar(url_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM urls WHERE id = ?", (url_id,))
    conn.commit()
    conn.close()
    flash("Enlace eliminado")
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='127.0.0.1', port=5000)
