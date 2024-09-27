# routes/student_routes.py
from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from models import get_db, find_user_by_id, get_aulas

student_bp = Blueprint('student', __name__)

@student_bp.route('/dashboard_aluno')
@student_bp.route('/dashboard_aluno')
def dashboard_aluno():
    user_id = session.get("user")
    if not user_id:
        return redirect(url_for('auth.login'))

    userData = find_user_by_id(user_id)
    aula = get_aulas(user_id)  # Pega a próxima aula disponível

    return render_template("dashboard_aluno.html", user=userData, aula=aula)


@student_bp.route('/ver_aula/<int:aula_id>', methods=["GET", "POST"])
def ver_aula(aula_id):
    user_id = session.get("user")
    if not user_id:
        return redirect(url_for('auth.login'))

    db = get_db()
    aula = db.execute('SELECT * FROM aulas WHERE id = ?', (aula_id,)).fetchone()

    if request.method == "POST":
        db.execute('INSERT INTO progresso_aulas (user_id, aula_id, concluida) VALUES (?, ?, 1)', 
                   (user_id, aula_id))
        db.commit()
        flash("Aula concluída com sucesso!", "success")
        return redirect(url_for('student.dashboard_aluno'))

    return render_template('ver_aula.html', aula=aula)
@student_bp.route('/concluir_aula/<int:aula_id>', methods=["POST"])
def concluir_aula(aula_id):
    if 'user' in session and session['tipo'] == 'aluno':
        user_id = session['user']
        
        db = get_db()
        
        # Marcar a aula como concluída
        db.execute(
            'INSERT OR REPLACE INTO progresso_atividades (user_id, section_id, aula_id, completou) VALUES (?, ?, ?, ?)',
            (user_id, 1, aula_id, 1)  # Supondo que section_id = 1 por enquanto
        )
        db.commit()
        
        flash("Aula concluída com sucesso!", "success")
        return redirect(url_for('student.dashboard_aluno'))
    
    return redirect(url_for('auth.login'))
