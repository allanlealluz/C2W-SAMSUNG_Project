from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from models import get_db, find_user_by_id
from utils import generate_plot
import sqlite3

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
@teacher_bp.route('/Criar_Aula', methods=["GET", "POST"])
def criarAula():
    if 'user' not in session or session['tipo'] != 'professor':
        return redirect(url_for('auth.login'))  # Redireciona para o login se o usuário não for professor

    if request.method == "POST":
        titulo = request.form.get("titulo")
        conteudo_nome = request.form.get("conteudo_nome")  # Obtenha o nome do conteúdo (se houver)
        descricao = request.form.get("descricao")
        topico = request.form.get("topico")  # Adiciona o tópico da aula

        if not titulo or not descricao or not topico:
            flash("Todos os campos são obrigatórios", "error")
            return redirect(url_for('teacher.criarAula'))

        db = get_db()
        try:
            db.execute('INSERT INTO aulas (professor_id, titulo, descricao, conteudo_nome, topico) VALUES (?, ?, ?, ?, ?)', 
                       (session['user'], titulo, descricao, conteudo_nome, topico))
            db.commit()
            flash("Aula criada com sucesso!", "success")
            return redirect(url_for('teacher.dashboard_professor'))  # Redireciona para o dashboard do professor
        except sqlite3.Error as e:
            flash(f"Erro ao criar a aula: {e}", "error")
            return redirect(url_for('teacher.criarAula'))

    return render_template("criarAula.html")