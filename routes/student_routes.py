# routes/student_routes.py
from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from models import get_db, find_user_by_id


student_bp = Blueprint('student', __name__)

@student_bp.route('/dashboard_aluno')
def dashboard_aluno():
    user_id = session.get("user")
    if not user_id:  
        return redirect(url_for('auth.login'))  # Redireciona para login se não estiver logado

    userData = find_user_by_id(user_id)
    return render_template("dashboard_aluno.html", user=userData)

@student_bp.route('/robotica')
def robotica():
    if 'user' in session:
        return render_template('aula1.html')
    return redirect(url_for('auth.login'))

@student_bp.route('/responder_atividade', methods=["POST", "GET"])
def responder_atividade():
    if 'user' in session and session['tipo'] == 'aluno':
        if request.method == "POST":
            resposta = request.form.get('resposta')
            section = request.form.get('section')

            if not resposta or not section:
                flash("Resposta ou seção não fornecida.", "error")
                return redirect(url_for('student.responder_atividade'))

            db = get_db()
            db.execute('INSERT INTO respostas (user_id, section, response) VALUES (?, ?, ?)', 
                       (session['user'], section, resposta))
            db.commit()
            flash("Resposta enviada com sucesso!", "success")
            return redirect(url_for('student.dashboard_aluno'))
        return render_template('responder_atividade.html')
    return redirect(url_for('auth.login'))

@student_bp.route('/update_progress', methods=["POST"])
def update_progress():
    if 'user' in session and session['tipo'] == 'aluno':
        if request.method == "POST":
            progresso = request.form.get('progresso')
            section_id = request.form.get('section_id')

            if not progresso or not section_id:
                flash("Progresso ou seção não fornecidos.", "error")
                return redirect(url_for('student.dashboard_aluno'))

            db = get_db()
            db.execute('INSERT INTO progresso_atividades (user_id, section_id, progress) VALUES (?, ?, ?)', 
                       (session['user'], section_id, progresso))
            db.commit()
            flash("Progresso atualizado com sucesso!", "success")
            return redirect(url_for('student.dashboard_aluno'))
    return redirect(url_for('auth.login'))
