# routes/student_routes.py
from flask import Blueprint, render_template, session, redirect, url_for
from models import get_db

student_bp = Blueprint('student', __name__)

@student_bp.route('/dashboard_aluno')
def dashboard_aluno():
    if 'user' in session and session['tipo'] == 'aluno':
        db = get_db()
        respostas = db.execute('SELECT * FROM respostas WHERE user_id = ?', (session['user'],)).fetchall()
        return render_template('dashboard_aluno.html', respostas=respostas)
    return redirect(url_for('auth.login'))

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
