import sqlite3
from flask import g

DATABASE = 'database.db'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        with open('schema.sql', 'r', encoding='utf-8') as f:
            sql_script = f.read()
        try:
            conn.executescript(sql_script)
            print("Banco de dados inicializado com sucesso!")
        except sqlite3.Error as e:
            print(f"Erro ao inicializar o banco de dados: {e}")

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
def get_aulas(user_id):
    db = get_db()
    
    # Obtém a próxima aula não concluída
    aula = db.execute('''
        SELECT aulas.id, aulas.titulo, aulas.descricao, aulas.conteudo 
        FROM aulas 
        LEFT JOIN progresso_aulas 
        ON aulas.id = progresso_aulas.aula_id AND progresso_aulas.user_id = ?
        WHERE progresso_aulas.id IS NULL
        ORDER BY aulas.id ASC 
        LIMIT 1
    ''', (user_id,)).fetchone()
    
    return aula
def verificar_tabelas():
    db = get_db()
    if db is None:
        print("Erro ao conectar ao banco de dados para verificar as tabelas.")
        return
    try:
        tabelas = db.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
        print("Tabelas encontradas:", [tabela["name"] for tabela in tabelas])
    except sqlite3.Error as e:
        print(f"Erro ao verificar tabelas: {e}")
if __name__ == '__main__':
    init_db()