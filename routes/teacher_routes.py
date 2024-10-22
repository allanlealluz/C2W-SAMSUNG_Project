from flask import Blueprint, render_template, session, redirect, url_for, request, flash
import os
import numpy as np
from werkzeug.utils import secure_filename
from models import get_db, find_user_by_id, criar_aula, get_aulas_by_professor, get_respostas_by_aula, get_progresso_by_aula, update_nota_resposta
from utils import generate_plot, kmeans_clustering, generate_cluster_plot, extract_keywords
import sqlite3

from flask import Blueprint, render_template, session, redirect, url_for, request, flash
import os
import numpy as np
from werkzeug.utils import secure_filename
from models import (
    get_db, 
    find_user_by_id, 
    criar_aula, 
    get_aulas_by_professor, 
    get_respostas_by_aula, 
    get_progresso_by_aula, 
    update_nota_resposta
)
from utils import generate_plot, kmeans_clustering, generate_cluster_plot, extract_keywords
import sqlite3

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

        conteudo_nome = None  # Inicializar como None
        conteudo_file = request.files.get('file')
        
        if conteudo_file and allowed_file(conteudo_file.filename):
            try:
                filename = secure_filename(conteudo_file.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                conteudo_file.save(filepath)
                conteudo_nome = filename
            except Exception as e:
                flash('Erro ao salvar o arquivo', 'error')
                return redirect(url_for('teacher.criarAula'))
        
        # Verifica se foi enviado um arquivo ou se o campo conteúdo foi preenchido
        if conteudo_nome is None and not request.form.get("conteudo"):
            flash("Você deve enviar um arquivo ou fornecer o conteúdo da aula.", "error")
            return redirect(url_for('teacher.criarAula'))

        conteudo = request.form.get("conteudo") if conteudo_nome is None else conteudo_nome
        
        try:
            criar_aula(user_id, titulo, descricao, conteudo, perguntas, topico, conteudo_nome)
            flash("Aula criada com sucesso!", "success")
            return redirect(url_for('teacher.dashboard_professor'))
        except sqlite3.Error as e:
            flash(f"Erro ao criar a aula: {e}", "error")
            return redirect(url_for('teacher.criarAula'))

    return render_template("criarAula.html")

@teacher_bp.route('/dashboard_professor/feedbacks')
def ver_feedbacks():
    if session.get('user') and session.get('tipo') == 'professor':
        user_id = session.get('user')
        aulas = get_aulas_by_professor(user_id)
        
        if not aulas:
            flash("Nenhuma aula encontrada para o professor.", "error")
            return redirect(url_for('teacher.dashboard_professor'))

        feedbacks = {}
        progresso_por_aluno = {}
        palavras_chave = {}
        total_alunos = set()

        for aula in aulas:
            aula_id = aula['id']
            titulo_aula = aula['titulo']
            respostas = get_respostas_by_aula(aula_id)

            if respostas is None:
                flash(f"Erro ao buscar respostas para a aula {titulo_aula}.", "error")
                continue
            
            feedbacks[titulo_aula] = respostas if respostas else []

            for resposta in respostas:
                nome_aluno = resposta['nome']
                pergunta_texto = resposta['pergunta_texto']
                keywords = extract_keywords(pergunta_texto)

                if nome_aluno not in palavras_chave:
                    palavras_chave[nome_aluno] = []
                palavras_chave[nome_aluno].extend(keywords)

            progresso = get_progresso_by_aula(aula_id)

            if progresso is None:
                flash(f"Erro ao buscar progresso para a aula {titulo_aula}.", "error")
                continue

            for aluno in progresso:
                nome = aluno['nome']
                total_alunos.add(nome)
                
                if nome not in progresso_por_aluno:
                    progresso_por_aluno[nome] = []
                progresso_por_aluno[nome].append(aluno['concluida'])

        alunos_data = {}
        alunos_completos = 0

        for nome, progresso_list in progresso_por_aluno.items():
            progresso_medio = min(max(sum(progresso_list) / len(progresso_list), 0), 1) * 100
            if all(progresso_list):
                alunos_completos += 1
            
            feedback_count = sum(1 for feedback_list in feedbacks.values() for f in feedback_list if f['nome'] == nome)
            alunos_data[nome] = [progresso_medio, feedback_count]

        alunos_incompletos = len(progresso_por_aluno) - alunos_completos

        # Verifica se há dados para clustering
        if alunos_data:
            X, labels, centroids = kmeans_clustering(alunos_data)
            plot_url = generate_cluster_plot(X, labels, centroids, list(alunos_data.keys())) if X is not None else None

        progresso_medio_total = sum(data[0] for data in alunos_data.values()) / len(alunos_data)
        alunos_abaixo_da_media = {nome: progresso_por_aluno[nome] for nome, data in alunos_data.items() if data[0] < progresso_medio_total}
        dificuldades = {nome: palavras_chave.get(nome, []) for nome in alunos_abaixo_da_media}

        return render_template(
            'feedbacks_professor.html',
            feedbacks=feedbacks,
            dificuldades=dificuldades,
            plot_respostas_url=plot_url,
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

    if update_nota_resposta(aluno, aula, nota):
        flash("Nota atribuída com sucesso!", "success")
    else:
        flash("Erro ao atribuir a nota.", "error")

    return redirect(url_for('teacher.ver_feedbacks'))
