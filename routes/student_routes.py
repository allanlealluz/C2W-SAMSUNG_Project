# routes/student_routes.py
from flask import Blueprint, render_template, session, redirect, url_for, request
from models import get_db, find_user_by_id


student_bp = Blueprint('student', __name__)

@student_bp.route('/dashboard_aluno')
def dashboard_aluno():
    user_id = session.get("user")
    if not user_id:
        return redirect(url_for('auth.login'))  # Redireciona para login se não estiver logado

    userData = find_user_by_id(user_id)
    return render_template("dashboard_aluno.html", user=userData)

@student_bp.route('/responder_atividade', methods=["POST", "GET"])
def responder_atividade():
    if 'user' in session and session['tipo'] == 'aluno':
        if request.method == "POST":
            resposta = request.form['resposta']
            section = request.form['section']
            db = get_db()
            db.execute('INSERT INTO respostas (user_id, section, response) VALUES (?, ?, ?)', (session['user'], section, resposta))
            db.commit()
            return redirect(url_for('student.dashboard_aluno'))
        return render_template('responder_atividade.html')
    return redirect(url_for('auth.login'))
