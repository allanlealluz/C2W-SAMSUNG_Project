from flask import Blueprint, render_template, session, redirect, url_for, request, flash, jsonify
from models import get_db, find_user_by_id, get_aulas, inscrever_aluno_curso

admin_bp = Blueprint('student', __name__)

@admin_bp.route('/dashboard_admin')
def dashboard_admin():
    if 'user' not in session or session['tipo'] != 'admin':
        return redirect(url_for('auth.login'))

    return render_template('dashboard_admin.html')

@admin_bp.route('/adicionar_curso', methods=["GET", "POST"])
def adicionar_curso():
    if 'user' not in session or session['tipo'] != 'admin':
        return redirect(url_for('auth.login'))

    if request.method == "POST":
        nome_curso = request.form.get("nome_curso")
        descricao = request.form.get("descricao")
        topico = request.form.get("topico")

        try:
            db = get_db()
            db.execute('''INSERT INTO cursos (nome, descricao, topico) VALUES (?, ?, ?)''', (nome_curso, descricao, topico))
            db.commit()
            print("Curso adicionado com sucesso!")
            return redirect(url_for('admin.dashboard_admin'))
        except Exception as e:
            print(f"Erro ao adicionar curso: {e}")
            return redirect(url_for('admin.adicionar_curso'))

    return render_template('adicionar_curso.html')


