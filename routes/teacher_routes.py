from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from models import get_db, find_user_by_id, criar_aula
import sqlite3
import os
import numpy as np
from werkzeug.utils import secure_filename
from utils import generate_plot, kmeans_clustering, generate_cluster_plot, extract_keywords


teacher_bp = Blueprint('teacher', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}  # Extensões permitidas
UPLOAD_FOLDER = os.path.join('static', 'uploads')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@teacher_bp.route('/dashboard_professor')
def dashboard_professor():
    user_id = session.get("user")
    if user_id and session['tipo'] == 'professor':
        userData = find_user_by_id(user_id) 
        return render_template('dashboard_professor.html', user=userData)
    return redirect(url_for('auth.login')) 

@teacher_bp.route('/Criar_Aula', methods=["GET", "POST"])
def criarAula():
    if 'user' not in session or session['tipo'] != 'professor':
        return redirect(url_for('auth.login')) 

    if request.method == "POST":
        titulo = request.form.get("titulo")
        descricao = request.form.get("descricao")
        topico = request.form.get("topico")
        user_id = session.get('user')
        
        perguntas = request.form.getlist("perguntas[]")

        if not titulo or not descricao or not topico:
            flash("Todos os campos são obrigatórios", "error")
            return redirect(url_for('teacher.criarAula'))
        
        conteudo_file = request.files.get('file')
        if conteudo_file and allowed_file(conteudo_file.filename):
            print(f"Arquivo recebido: {conteudo_file.filename}")
            try:
                filename = secure_filename(conteudo_file.filename)
                # Define o caminho completo para salvar o arquivo dentro de 'static/uploads'
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                conteudo_file.save(filepath)
                conteudo_nome = filename
            except Exception as e:
                print('Erro ao salvar o arquivo:', e)
                flash('Erro ao salvar o arquivo', 'error')
                return redirect(url_for('teacher.criarAula'))
        else:
            flash("Formato de arquivo inválido ou nenhum arquivo foi enviado.", "error")
            return redirect(url_for('teacher.criarAula'))

        try:

            criar_aula(user_id, titulo, descricao, conteudo_nome, perguntas, topico, filename)
            flash("Aula criada com sucesso!", "success")
            return redirect(url_for('teacher.dashboard_professor'))
        except sqlite3.Error as e:
            flash(f"Erro ao criar a aula: {e}", "error")
            return redirect(url_for('teacher.criarAula'))

    return render_template("criarAula.html")

@teacher_bp.route('/dashboard_professor/feedbacks')
def ver_feedbacks():
    if 'user' in session and session['tipo'] == 'professor':
        db = get_db()
        user_id = session.get('user')

        aulas = db.execute('''SELECT id, titulo FROM aulas WHERE professor_id = ?''', (user_id,)).fetchall()

        feedbacks = {}
        progresso_por_aluno = {}
        palavras_chave = {}
        total_alunos = set()

        for aula in aulas:
            aula_id = aula['id']
            titulo_aula = aula['titulo']
            
            respostas = db.execute('''
                SELECT usuarios.nome, respostas.pergunta_id, respostas.resposta, perguntas.texto AS pergunta_texto
                FROM respostas
                JOIN usuarios ON respostas.user_id = usuarios.id
                JOIN perguntas ON respostas.pergunta_id = perguntas.id
                WHERE respostas.aula_id = ?
            ''', (aula_id,)).fetchall()

            feedbacks[titulo_aula] = respostas

            for resposta in respostas:
                nome_aluno = resposta['nome']
                pergunta_texto = resposta['pergunta_texto']
                keywords = extract_keywords(pergunta_texto)
                
                if nome_aluno not in palavras_chave:
                    palavras_chave[nome_aluno] = []
                palavras_chave[nome_aluno].extend(keywords)

            progresso = db.execute('''
                SELECT usuarios.nome, progresso_aulas.concluida
                FROM progresso_aulas
                JOIN usuarios ON progresso_aulas.user_id = usuarios.id
                WHERE progresso_aulas.aula_id = ?
            ''', (aula_id,)).fetchall()

            for aluno in progresso:
                nome = aluno['nome']
                total_alunos.add(nome)
                if nome not in progresso_por_aluno:
                    progresso_por_aluno[nome] = []
                progresso_por_aluno[nome].append(aluno['concluida'])

        alunos_data = {}
        alunos_completos = 0
        for nome, progresso_list in progresso_por_aluno.items():
            progresso_medio = np.clip(np.mean(progresso_list), 0, 1) * 100

            if all(progresso_list):
                alunos_completos += 1
            
            feedback_count = sum(1 for feedback_list in feedbacks.values() for f in feedback_list if f['nome'] == nome)
            alunos_data[nome] = [progresso_medio, feedback_count]

        alunos_incompletos = len(progresso_por_aluno) - alunos_completos

        X, labels, centroids = kmeans_clustering(alunos_data)

        if X is not None:
            nomes_alunos = list(alunos_data.keys())
            plot_url = generate_cluster_plot(X, labels, centroids, nomes_alunos)

        progresso_medio_total = np.mean([data[0] for data in alunos_data.values()])
        alunos_abaixo_da_media = {nome: progresso_por_aluno[nome] for nome, data in alunos_data.items() if data[0] < progresso_medio_total}
        dificuldades = {nome: palavras_chave.get(nome, []) for nome in alunos_abaixo_da_media}

        return render_template(
            'feedbacks_professor.html',
            feedbacks=feedbacks,
            dificuldades=dificuldades,
            plot_respostas_url='/static/images/cluster_plot.png',
            progresso=progresso_por_aluno,
            alunos_completos=alunos_completos,
            alunos_incompletos=alunos_incompletos
        )
    return redirect(url_for('auth.login'))

@teacher_bp.route('/dar_nota', methods=['POST'])
def dar_nota():
    aluno = request.form['aluno']
    aula = request.form['aula']
    nota = int(request.form['nota'])

    db = get_db()
    db.execute('''
        UPDATE respostas
        SET nota = ?
        WHERE user_id = (SELECT id FROM usuarios WHERE nome = ?) AND aula_id = (SELECT id FROM aulas WHERE titulo = ?)
    ''', (nota, aluno, aula))
    db.commit()

    return redirect(url_for('feedbacks_professor'))
