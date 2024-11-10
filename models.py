import sqlite3
from flask import g
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
        
def inscrever_aluno_curso(aluno_id, curso_id):
    db = get_db()
    if db is None:
        return "erro"
    inscricao = db.execute(
        "SELECT * FROM inscricoes WHERE aluno_id = ? AND curso_id = ?", 
        (aluno_id, curso_id)
    ).fetchone()

    if inscricao:
        print("Aluno já inscrito neste curso.")
        return "inscrito"

    try:
        db.execute(
            "INSERT INTO inscricoes (aluno_id, curso_id) VALUES (?, ?)", 
            (aluno_id, curso_id)
        )
        db.commit()
        print("Inscrição realizada com sucesso!")
        return "sucesso"
    except sqlite3.Error as e:
        print(f"Erro ao inscrever aluno no curso: {e}")
        return "erro"

def get_aulas_por_modulo(modulo_id):
    db = get_db()
    return db.execute('SELECT * FROM aulas WHERE modulo_id = ?', (modulo_id,)).fetchall()

def atualizar_progresso_atividade(user_id, modulo_id, aula_id, completou):
    db = get_db()
    if db is None:
        return "erro"
    try:
        db.execute('INSERT OR REPLACE INTO progresso_atividades (user_id, modulo_id, aula_id, completou) VALUES (?, ?, ?, ?)', 
                   (user_id, modulo_id, aula_id, completou))
        db.commit()
    except sqlite3.Error as e:
        print(f"Erro ao atualizar progresso: {e}")

def atualizar_progresso_curso(user_id, curso_id, progresso):
    db = get_db()
    if db is None:
        return "erro"
    try:
        db.execute('INSERT OR REPLACE INTO progresso_cursos (user_id, curso_id, progresso) VALUES (?, ?, ?)', 
                   (user_id, curso_id, progresso))
        db.commit()
    except sqlite3.Error as e:
        print(f"Erro ao atualizar progresso do curso: {e}")

def get_progresso_por_aula(aula_id):
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
def get_modulos_by_professor(professor_id):
    db = get_db()
    try:
        modulos = db.execute('''
            SELECT id, titulo
            FROM modulos
            WHERE professor_id = ?
        ''', (professor_id,)).fetchall()
        return modulos
    except sqlite3.Error as e:
        print(f"Erro ao buscar módulos: {e}")
        return []

def update_nota_resposta(resposta_id, nota):
    db = get_db()
    try:
        db.execute('UPDATE respostas SET nota = ? WHERE id = ?', (nota, resposta_id))
        db.commit()
    except sqlite3.Error as e:
        print(f"Erro ao atualizar nota: {e}")
        print(f"Erro ao atualizar progresso: {e}")

def create_module(curso_id, titulo, descricao):
    db = get_db()
    try:
        db.execute('INSERT INTO modulos (curso_id, titulo, descricao) VALUES (?, ?, ?)', (curso_id, titulo, descricao))
        db.commit()
    except sqlite3.Error as e:
        print(f"Erro ao criar módulo: {e}")

def criar_aula(modulo_id,curso_id, titulo, descricao, conteudo_nome, perguntas, arquivo):
    db = get_db()
    if db is None:
        return None
    try:
        db.execute('INSERT INTO aulas (modulo_id,curso_id, titulo, descricao, conteudo_nome, arquivo) VALUES (?, ?, ?,?, ?, ?)',
                   (modulo_id,curso_id, titulo, descricao, conteudo_nome, arquivo))
        aula_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
        
        for pergunta in perguntas:
            db.execute('INSERT INTO perguntas (aula_id, texto) VALUES (?, ?)', (aula_id, pergunta))
        
        db.commit()
        print("Aula e perguntas criadas com sucesso!")
    except sqlite3.Error as e:
        db.rollback()
        print(f"Erro ao criar aula: {e}")
        return None
def criar_modulos(curso_id, titulo, descricao, professor_id):
    db = get_db()
    try:
        db.execute('''
            INSERT INTO modulos (curso_id, titulo, descricao, professor_id)
            VALUES (?, ?, ?, ?)
        ''', (curso_id, titulo, descricao, professor_id))
        db.commit()
        print("Módulo criado com sucesso!")

    except sqlite3.Error as e:
        print(f"Erro ao criar módulo: {e}")
        db.rollback()
def get_cursos():
    db = get_db()
    cursos = db.execute('SELECT * FROM cursos').fetchall()
    return cursos
def get_modulos_by_curso_id(curso_id):
    db = get_db()
    curso = db.execute('SELECT id,titulo,descricao, curso_id FROM modulos WHERE curso_id = ?', (curso_id,)).fetchall()
    return curso
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
    db = get_db()
    if db is None:
        print("Erro ao conectar ao banco de dados para verificar as tabelas.")
        return
    try:
        return db.execute("""
        SELECT a.* 
        FROM aulas a
        JOIN modulos m ON a.modulo_id = m.id
        JOIN cursos c ON a.curso_id = c.id
        WHERE c.professor_id = ?
    """, (user_id,)).fetchall()
    except sqlite3.Error as e:
        print(f"Erro ao verificar tabelas: {e}")
    return None
def get_respostas_by_aula(aula_id):
    db = get_db()
    return db.execute('''
        SELECT r.user_id, u.nome, r.resposta,r.nota
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
    return db.execute("SELECT * FROM usuarios where tipo != 'professor' and tipo != 'admin'").fetchall()
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
    db = get_db() 
    if db is None:
        return []
     
    cursor = db.cursor()
    query = """
    SELECT 
        r.user_id, 
        u.nome, 
        r.nota, 
        pa.concluida,  -- Status de conclusão da aula
        a.titulo AS aula_conteudo
    FROM 
        respostas r
        JOIN aulas a ON r.aula_id = a.id
        JOIN usuarios u ON r.user_id = u.id
        JOIN progresso_aulas pa ON pa.user_id = u.id AND pa.aula_id = a.id;
    """
    
    cursor.execute(query)
    scores = cursor.fetchall()
    alunos_data = []
    for aluno_id, nome, nota, concluida, aula in scores:
        progresso = 1 if concluida else 0 
        alunos_data.append((aluno_id, nome, nota, progresso, aula))

    return alunos_data

def get_student_scores_topic():
    conn = get_db()
    cursor = conn.cursor()

    query = """
    SELECT 
        r.user_id, 
        u.nome, 
        r.nota, 
        pa.concluida, 
        a.topico AS aula_conteudo
    FROM 
        respostas r
        JOIN aulas a ON r.aula_id = a.id
        JOIN usuarios u ON r.user_id = u.id
        JOIN progresso_aulas pa ON pa.user_id = u.id AND pa.aula_id = a.id;
    """
    
    cursor.execute(query)
    scores = cursor.fetchall()
    alunos_data = []
    for aluno_id, nome, nota, concluida, topico in scores:
        progresso = 1 if concluida else 0
        alunos_data.append((aluno_id, nome, nota, progresso, topico))

    conn.close()
    return alunos_data

if __name__ == '__main__':
    init_db()
