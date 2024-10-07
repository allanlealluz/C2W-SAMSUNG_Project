from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from models import get_db, find_user_by_id, get_aulas

student_bp = Blueprint('student', __name__)

# Rota para o dashboard do aluno
@student_bp.route('/dashboard_aluno')
def dashboard_aluno():
    user_id = session.get("user")
    if not user_id:
        return redirect(url_for('auth.login'))

    userData = find_user_by_id(user_id)
    aula = get_aulas(user_id)  # Pega a próxima aula disponível

    return render_template("dashboard_aluno.html", user=userData, aula=aula)


# Rota para visualizar a aula
@student_bp.route('/ver_aula/<int:aula_id>', methods=["GET", "POST"])
def ver_aula(aula_id):
    user_id = session.get("user")
    if not user_id:
        return redirect(url_for('auth.login'))

    db = get_db()
    aula = db.execute('SELECT * FROM aulas WHERE id = ?', (aula_id,)).fetchone()

    if request.method == "POST":
        # Marcar aula como concluída
        db.execute('INSERT INTO progresso_aulas (user_id, aula_id, concluida) VALUES (?, ?, 1)', 
                   (user_id, aula_id))
        db.commit()
        flash("Aula concluída com sucesso!", "success")
        return redirect(url_for('student.dashboard_aluno'))

    return render_template('ver_aula.html', aula=aula)


# Rota para concluir a aula
@student_bp.route('/concluir_aula/<int:aula_id>', methods=["POST"])
def concluir_aula(aula_id):
    if 'user' in session and session['tipo'] == 'aluno':
        user_id = session['user']
        
        db = get_db()
        
        # Marcar a aula como concluída na tabela de progresso
        db.execute(
            'INSERT OR REPLACE INTO progresso_atividades (user_id, section_id, aula_id, completou) VALUES (?, ?, ?, ?)',
            (user_id, 1, aula_id, 1)  # Supondo que section_id = 1 por enquanto
        )
        db.commit()
        
        flash("Aula concluída com sucesso!", "success")
        return redirect(url_for('student.dashboard_aluno'))
    
    return redirect(url_for('auth.login'))
# Rota para responder a aula
@student_bp.route('/responder_aula/<int:aula_id>', methods=["POST"])
def responder_atividade(aula_id):
    user_id = session.get("user")
    if not user_id:
        return redirect(url_for('auth.login'))

    db = get_db()
    
    # Pega a resposta do formulário
    resposta = request.form.get('resposta')
    
    if resposta:
        # Salvar a resposta no banco de dados
        db.execute(
            'INSERT INTO respostas_aulas (user_id, aula_id, resposta) VALUES (?, ?, ?)',
            (user_id, aula_id, resposta)
        )
        db.commit()
        
        flash("Resposta enviada com sucesso!", "success")
    else:
        flash("Por favor, insira uma resposta.", "danger")

    return redirect(url_for('student.ver_aula', aula_id=aula_id))