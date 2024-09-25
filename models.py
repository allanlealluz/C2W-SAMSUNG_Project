import sqlite3
from flask import g

DATABASE = 'database.db'

def get_db():
    if 'db' not in g:
        try:
            g.db = sqlite3.connect(DATABASE)
            g.db.row_factory = sqlite3.Row
        except sqlite3.Error as e:
            print(f"Erro ao conectar ao banco de dados: {e}")
            return None
    return g.db

def create_user(nome, email, senha, tipo):
    db = get_db()
    if db is None:
        return "erro"
    try:
        db.execute('INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)', (nome, email, senha, tipo))
        db.commit()
    except sqlite3.Error as e:
        print(f"Erro ao criar usuário: {e}")

def find_user(email):
    db = get_db()
    if db is None:
        return None

    try:
        return db.execute('SELECT * FROM usuarios WHERE email = ?', (email,)).fetchone()
    except sqlite3.Error as e:
        print(f"Erro ao buscar usuário: {e}")
        return None

def find_user_by_id(id):
    db = get_db()
    if db is None:
        return None
    try:
        return db.execute('SELECT * FROM usuarios WHERE id = ?', (id,)).fetchone()
    except sqlite3.Error as e:
        print(f"Erro ao buscar usuário por ID: {e}")
        return None
def inserir_resposta(user_id, section, resposta, aula_id):
    db = get_db()
    if db is None:
        return "erro"
    try:
        db.execute('INSERT INTO respostas (user_id, section, response, aula_id) VALUES (?, ?, ?, ?)', 
                   (user_id, section, resposta, aula_id))
        db.commit()
    except sqlite3.Error as e:
        print(f"Erro ao inserir resposta: {e}")

def atualizar_progresso(user_id, section_id, aula_id, completou):
    db = get_db()
    if db is None:
        return "erro"
    try:
        db.execute('INSERT OR REPLACE INTO progresso_atividades (user_id, section_id, aula_id, completou) VALUES (?, ?, ?, ?)', 
                   (user_id, section_id, aula_id, completou))
        db.commit()
    except sqlite3.Error as e:
        print(f"Erro ao atualizar progresso: {e}")

def criar_aula(professor_id, titulo, descricao, conteudo_nome, topico):
    db = get_db()
    if db is None:
        return None
    try:
        db.execute('INSERT INTO aulas (professor_id, titulo, descricao, conteudo_nome, topico) VALUES (?, ?, ?, ?, ?)', 
                   (professor_id, titulo, descricao, conteudo_nome, topico))
        db.commit()
    except sqlite3.Error as e:
        print(f"Erro ao criar aula: {e}")
