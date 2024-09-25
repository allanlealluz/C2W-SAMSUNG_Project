from flask import Blueprint, render_template, session, redirect, url_for
from models import get_db, find_user_by_id
from utils import generate_plot

teacher_bp = Blueprint('teacher', __name__)

@teacher_bp.route('/dashboard_professor')
def dashboard_professor():
    user_id = session.get("user")
    if user_id and session['tipo'] == 'professor':
         userData = find_user_by_id(user_id) 
         return render_template('dashboard_professor.html',user=userData)
    return redirect(url_for('auth.login'))     
@teacher_bp.route('/dashboard_professor/feedbacks')
def ver_feedbacks():
    if 'user' in session and session['tipo'] == 'professor':
        db = get_db()
        respostas = db.execute(''' 
            SELECT usuarios.nome, respostas.section, respostas.response
            FROM respostas 
            JOIN usuarios ON respostas.user_id = usuarios.id
        ''').fetchall()
        
        respostas_por_aluno = {}
        for resposta in respostas:
            nome = resposta['nome']
            if nome not in respostas_por_aluno:
                respostas_por_aluno[nome] = 0
            respostas_por_aluno[nome] += 1
        
        plot_respostas_url = generate_plot(respostas_por_aluno, 'Quantidade de Respostas por Aluno', 'Alunos', 'Respostas')

        return render_template('feedbacks_professor.html', plot_respostas_url=plot_respostas_url)
    
    return redirect(url_for('auth.login'))
