import sqlite3
from flask import g
from collections import defaultdict
import numpy as np
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
def execute_query(query, params=None):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if query.strip().lower().startswith("select"):
            result = cursor.fetchall()
        else:
            conn.commit()
            result = cursor.lastrowid  

        return result
    except sqlite3.Error as e:
        print(f"Erro ao executar query: {e}")
        return None
    finally:
        cursor.close()
        conn.close()
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

def criar_aula(professor_id, titulo, descricao, conteudo_nome, perguntas, topico, arquivo):
    db = get_db()
    if db is None:
        return None
    try:
        db.execute('''INSERT INTO aulas (professor_id, titulo, descricao, conteudo_nome, topico, arquivo) 
                      VALUES (?, ?, ?, ?, ?, ?)''', (professor_id, titulo, descricao, conteudo_nome, topico, arquivo))
        
        aula_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
        
        for pergunta in perguntas:
            db.execute('''INSERT INTO perguntas (aula_id, texto) VALUES (?, ?)''', (aula_id, pergunta))
        
        db.commit()
        print("Aula e perguntas criadas com sucesso!")
    except sqlite3.Error as e:
        db.rollback()
        print(f"Erro ao criar aula: {e}")
        return None
    
def get_aulas(user_id):
    db = get_db()
    aula = db.execute('''SELECT aulas.id, aulas.titulo, aulas.descricao, aulas.conteudo_nome, aulas.arquivo 
                         FROM aulas 
                         LEFT JOIN progresso_aulas 
                         ON aulas.id = progresso_aulas.aula_id AND progresso_aulas.user_id = ?
                         WHERE progresso_aulas.id IS NULL
                         ORDER BY aulas.id''', (user_id,)).fetchone()
    
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
        
def get_aulas_by_professor(user_id, topico=None):
    query = "SELECT * FROM aulas WHERE professor_id = ?"
    params = [user_id]

    if topico:
        query += " AND topico = ?"
        params.append(topico)

    return execute_query(query, params)

def get_respostas_by_aula(aula_id):
    db = get_db()
    return db.execute('''
        SELECT r.user_id, u.nome, r.resposta
        FROM respostas r
        JOIN usuarios u ON r.user_id = u.id
        WHERE r.aula_id = ?
    ''', (aula_id,)).fetchall()

def get_resposta_by_aluno_aula(aluno_id, aula_id):
    db = get_db()
    return db.execute('''
        SELECT r.user_id, u.nome, r.resposta
        FROM respostas r
        JOIN usuarios u ON r.user_id = u.id
        WHERE r.aula_id = ? AND r.user_id = ?
    ''', (aula_id, aluno_id)).fetchone()


def get_alunos():
    db = get_db()
    return db.execute("SELECT * FROM usuarios where tipo != 'professor'").fetchall()
def resp_aluno(aluno_id):
      db = get_db()
      return db.execute("SELECT * FROM respostas where user_id = ?", (aluno_id,)).fetchall()

def get_progresso_by_aula(aula_id):
    db = get_db()
    try:
        return db.execute('''
            SELECT usuarios.nome, progresso_aulas.concluida
            FROM progresso_aulas
            JOIN usuarios ON progresso_aulas.user_id = usuarios.id
            WHERE progresso_aulas.aula_id = ?
        ''', (aula_id,)).fetchall()
    except sqlite3.Error as e:
        print(f"Erro ao buscar progresso: {e}")
        return None

def update_nota_resposta(resposta_id, nota):
    db = get_db()
    try:
        db.execute('''
            UPDATE respostas
            SET nota = ?
            WHERE id = ?
        ''', (nota, resposta_id))
        db.commit()
    except sqlite3.Error as e:
        print(f"Erro ao atualizar nota: {e}") 

def Adicionar_nota(aula_id, aluno_id, nota):
    db = get_db()
    try:
        db.execute('''
            UPDATE respostas
            SET nota = ?
            WHERE aula_id = ? AND user_id = ?
        ''', (nota, aula_id, aluno_id))
        db.commit()
    except sqlite3.Error as e:
        print(f"Erro ao atualizar nota: {e}")
def get_student_scores():
    conn = get_db()
    cursor = conn.cursor()

    query = """
    SELECT 
        r.user_id, 
        u.nome, 
        r.nota, 
        a.titulo AS aula_conteudo
    FROM 
        respostas r
        JOIN aulas a ON r.aula_id = a.id
        JOIN usuarios u ON r.user_id = u.id; 
    """
    
    cursor.execute(query)
    scores = cursor.fetchall()
    alunos_data = []
    for aluno_id, nome, nota, topico in scores:
        alunos_data.append((aluno_id, nome, nota, topico))

    conn.close()
    return alunos_data
def get_student_scores_topic():
    conn = get_db()
    cursor = conn.cursor()

    query = """
    SELECT 
        r.user_id, 
        u.nome, 
        r.nota, 
        a.topico AS aula_conteudo
    FROM 
        respostas r
        JOIN aulas a ON r.aula_id = a.id
        JOIN usuarios u ON r.user_id = u.id; 
    """
    
    cursor.execute(query)
    scores = cursor.fetchall()
    alunos_data = []
    for aluno_id, nome, nota, topico in scores:
        alunos_data.append((aluno_id, nome, nota, topico))

    conn.close()
    return alunos_data

if __name__ == '__main__':
    init_db()
