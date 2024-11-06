from flask import Blueprint, render_template, session, redirect, url_for, request, flash, jsonify
from models import get_db, find_user_by_id

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard_admin')
def dashboard_admin():
    user_id = session.get("user")
    if not user_id or session.get("tipo") != "admin":
        return redirect(url_for('auth.login'))

    user_info = find_user_by_id(user_id)
    return render_template('dashboard_admin.html', user=user_info)

# Função para criar um novo curso
@admin_bp.route('/dashboard_admin/criar_curso', methods=['GET', 'POST'])
def criar_curso():
    user_id = session.get("user")
    if not user_id or session.get("tipo") != "admin":
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        # Obter os dados do formulário
        titulo = request.form['titulo']
        descricao = request.form['descricao']

        # Verificação simples para garantir que os campos não estejam vazios
        if not titulo or not descricao:
            return render_template("criar_curso.html", message="Todos os campos são obrigatórios!")

        # Inserir o novo curso no banco de dados
        db = get_db()
        db.execute('''
            INSERT INTO cursos (nome, descricao) 
            VALUES (?, ?)
        ''', (titulo, descricao))
        db.commit()

        # Redirecionar para o dashboard do admin após criar o curso
        return redirect(url_for('admin.dashboard_admin'))

    return render_template('criar_curso.html')

# Função para gerenciar os usuários
@admin_bp.route('/dashboard_admin/gerenciar_usuarios')
def gerenciar_usuarios():
    user_id = session.get("user")
    if not user_id or session.get("tipo") != "admin":
        return redirect(url_for('auth.login'))

    db = get_db()
    usuarios = db.execute('SELECT id, nome, email, tipo FROM usuarios').fetchall()
    return render_template('gerenciar_usuarios.html', usuarios=usuarios)

# Função para alterar o tipo de usuário (por exemplo, promover um usuário a professor)
@admin_bp.route('/dashboard_admin/alterar_usuario/<int:user_id>', methods=['POST'])
def alterar_usuario(user_id):
    user_tipo = request.form['tipo']

    db = get_db()
    db.execute('''
        UPDATE usuarios
        SET tipo = ?
        WHERE id = ?
    ''', (user_tipo, user_id))
    db.commit()

    return redirect(url_for('admin.gerenciar_usuarios'))