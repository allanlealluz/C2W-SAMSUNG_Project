import sqlite3
from flask import g, current_app

DATABASE = 'database.db'

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    with current_app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

def create_user(nome, email, senha, tipo):
    db = get_db()
    db.execute('INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)', (nome, email, senha, tipo))
    db.commit()

def find_user(email):
    db = get_db()
    return db.execute('SELECT * FROM usuarios WHERE email = ?', (email,)).fetchone()

def find_user_by_id(id):
    db = get_db()
    return db.execute('SELECT * FROM usuarios WHERE id = ?', (id,)).fetchall()

