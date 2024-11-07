from flask import Blueprint, render_template, session, redirect, url_for, request, flash, jsonify
from models import get_db, find_user_by_id, get_cursos
from hashlib import sha256
import sqlite3

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard_admin')
def dashboard_admin():
    user_id = session.get("user")
    if not user_id or session.get("tipo") != "admin":
        return redirect(url_for('auth.login'))

    user_info = find_user_by_id(user_id)
    return render_template('dashboard_admin.html', user=user_info)

@admin_bp.route('/dashboard_admin/criar_curso', methods=['GET', 'POST'])
def criar_curso():
    user_id = session.get("user")
    if not user_id or session.get("tipo") != "admin":
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        titulo = request.form['titulo']
        descricao = request.form['descricao']

        if not titulo or not descricao:
            return render_template("criar_curso.html", message="Todos os campos são obrigatórios!")

        db = get_db()
        db.execute('''
            INSERT INTO cursos (nome, descricao) 
            VALUES (?, ?)
        ''', (titulo, descricao))
        db.commit()

        return redirect(url_for('admin.dashboard_admin'))

    return render_template('criar_curso.html')

@admin_bp.route('/dashboard_admin/gerenciar_cursos', methods=["GET", "POST"])
def gerenciar_cursos():
    if 'user' not in session or session['tipo'] != 'admin':
        return redirect(url_for('auth.login'))

    try:
        cursos = get_cursos()
    except sqlite3.Error as e:
        print(f"Erro ao buscar cursos: {e}", "error")
        cursos = []

    return render_template("gerenciar_curso.html", cursos=cursos)

@admin_bp.route('/dashboard_admin/gerenciar_usuarios')
def gerenciar_usuarios():
    user_id = session.get("user")
    if not user_id or session.get("tipo") != "admin":
        return redirect(url_for('auth.login'))

    try:
        db = get_db()
        usuarios = db.execute('SELECT id, nome, email, tipo FROM usuarios').fetchall()
        usuarios = [dict(id=user[0], nome=user[1], email=user[2], tipo=user[3]) for user in usuarios]
    except sqlite3.Error as e:
        print(f"Erro ao buscar usuários: {e}")
        usuarios = []

    return render_template('gerenciar_usuarios.html', usuarios=usuarios)

@admin_bp.route('/dashboard_admin/alterar_usuario/<int:user_id>', methods=['POST'])
def alterar_usuario(user_id):
    if 'user' not in session or session['tipo'] != 'admin':
        return redirect(url_for('auth.login'))

    user_tipo = request.form['tipo']
    db = get_db()
    db.execute('''
        UPDATE usuarios
        SET tipo = ?
        WHERE id = ?
    ''', (user_tipo, user_id))
    db.commit()

    flash("Tipo de usuário atualizado com sucesso.")
    return redirect(url_for('admin.gerenciar_usuarios'))

@admin_bp.route('/dashboard_admin/excluir_usuario/<int:user_id>', methods=['POST'])
def excluir_usuario(user_id):
    if 'user' not in session or session['tipo'] != 'admin':
        return redirect(url_for('auth.login'))

    db = get_db()
    db.execute('DELETE FROM usuarios WHERE id = ?', (user_id,))
    db.commit()

    flash("Usuário excluído com sucesso.")
    return redirect(url_for('admin.gerenciar_usuarios'))

def editar_curso(curso_id):
    if request.method == "POST":
        novo_nome = request.form["nome"]
        nova_descricao = request.form["descricao"]

        db = get_db()
        db.execute('''
            UPDATE cursos
            SET nome = ?, descricao = ?
            WHERE id = ?
        ''', (novo_nome, nova_descricao, curso_id))
        db.commit()
        
        return redirect(url_for("admin.gerenciar_cursos"))

    curso = get_curso_by_id(curso_id)
    return render_template("editar_curso.html", curso=curso)

@admin_bp.route('/dashboard_admin/excluir_curso/<int:curso_id>', methods=["POST","GET"])
def excluir_curso(curso_id):
    db = get_db()
    db.execute('DELETE FROM cursos WHERE id = ?', (curso_id,))
    db.commit()
    return redirect(url_for('admin.gerenciar_cursos'))

@admin_bp.route('/dashboard_admin/cadastrar_professor', methods=['GET', 'POST'])
def cadastrar_professor():
    if 'user' not in session or session['tipo'] != 'admin':
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        
        senha_hash = sha256(senha.encode('utf-8')).hexdigest() 
        db = get_db()
        try:
            db.execute('''
                INSERT INTO usuarios (nome, email, senha, tipo)
                VALUES (?, ?, ?, ?)
            ''', (nome, email, senha_hash, 'professor'))
            db.commit()
            flash('Professor cadastrado com sucesso!')
            return redirect(url_for('admin.gerenciar_usuarios'))
        except sqlite3.IntegrityError:
            flash('Erro: o email já está em uso. Tente outro.')
            return redirect(url_for('admin.cadastrar_professor'))

    return render_template('cadastrar_professor.html')

def get_curso_by_id(curso_id):
    db = get_db()
    curso = db.execute('SELECT id, nome, descricao FROM cursos WHERE id = ?', (curso_id,)).fetchone()
    if curso:
        return dict(id=curso[0], nome=curso[1], descricao=curso[2])
    return None
