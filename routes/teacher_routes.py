from flask import Blueprint, render_template, session, redirect, url_for, request, flash, jsonify
import os
import numpy as np
from werkzeug.utils import secure_filename
from models import get_db, find_user_by_id, criar_aula, get_aulas_by_professor, get_respostas_by_aula, get_progresso_by_aula, get_alunos, Adicionar_nota, resp_aluno
from utils import  generate_performance_plot
import sqlite3

teacher_bp = Blueprint('teacher', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}
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

        conteudo_nome = None  
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
        total_alunos = set()

        for aula in aulas:
            aula_id = aula[0]
            titulo_aula = aula[1]  

            respostas = get_respostas_by_aula(aula_id)

            if respostas is None:
                flash(f"Erro ao buscar respostas para a aula {titulo_aula}.", "error")
                continue

            feedbacks[titulo_aula] = respostas if respostas else []

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
        for nome, progresso_list in progresso_por_aluno.items():
            print(progresso_list)
            alunos_data[nome] = progresso_list

        plot_url, previsoes = (None, None)

        if alunos_data:
            plot_url, previsoes = generate_performance_plot(alunos_data)

        alunos_completos = sum(all(prog) for prog in progresso_por_aluno.values())
        alunos_incompletos = len(progresso_por_aluno) - alunos_completos

        progresso_medio_total = sum(sum(data) / len(data) for data in alunos_data.values()) / len(alunos_data)
        print(respostas)
        resp =  get_respostas_by_aula(aula_id)
        return render_template(
            'feedbacks_professor.html',
            feedbacks=feedbacks,
            respostas = resp,
            plot_respostas_url=plot_url,
            previsoes=previsoes,
            progresso=progresso_por_aluno,
            alunos_completos=alunos_completos,
            alunos_incompletos=alunos_incompletos,
            progresso_medio_total=progresso_medio_total,
            aula_id = aula_id
        )

    return redirect(url_for('auth.login'))

@teacher_bp.route('/dashboard_professor/avaliar_alunos', methods=["GET"])
def avaliar_alunos():
    if 'user' not in session or session['tipo'] != 'professor':
        return redirect(url_for('auth.login'))
    
    alunos = get_alunos()
    
    return render_template('avaliar_alunos.html', alunos=alunos)


@teacher_bp.route('/dashboard_professor/analisar_aluno/<int:aluno_id>', methods=["GET", "POST"])
def analisar_aluno(aluno_id):
    if 'user' not in session or session['tipo'] != 'professor':
        return redirect(url_for('auth.login'))

    if request.method == "POST":
        nota = request.form.get('nota')
        if nota:
            Adicionar_nota(1,aluno_id, nota)
            flash("Nota adicionada com sucesso!", "success")
            return redirect(url_for('teacher.avaliar_alunos'))

    # Busca as respostas do aluno específico
    resposta = resp_aluno(aluno_id)
    print([resp['resposta'] for resp in resposta])
    return render_template('analisar_aluno.html', resposta=resposta, aluno_id=aluno_id)

@teacher_bp.route('/dashboard_professor/update_nota_resposta', methods=["GET", "POST"])
def update_nota_resposta_route():
    data = request.get_json()
    resposta_id = data.get("resposta_id")
    nota = data.get("nota")

    if resposta_id and nota is not None:
        update_nota_resposta(resposta_id, nota)
        return jsonify({"success": True}), 200
    return jsonify({"error": "Dados inválidos"}), 400

@teacher_bp.route('/dashboard_professor/analisar_desempenho', methods=["GET"])
def analisar_desempenho():
    if 'user' not in session or session['tipo'] != 'professor':
        return redirect(url_for('auth.login'))

    # Obter notas dos alunos
    alunos_data = get_student_scores()
    print(alunos_data)

    if not alunos_data:
        flash("Nenhum dado disponível para análise.", "error")
        return redirect(url_for('teacher.dashboard_professor'))
    
    # Agrupar os alunos usando K-Means
    X, labels, centroids = kmeans_clustering(alunos_data)

    # Verifique se X, labels e centroids são válidos antes de gerar o gráfico
    if X is None or labels is None or centroids is None:
        flash("Erro ao realizar clustering. Verifique os dados.", "error")
        return redirect(url_for('teacher.dashboard_professor'))

    # Gerar o gráfico dos clusters
    plot_url = generate_cluster_plot(X, labels, centroids, alunos_data)
    print(plot_url)
    return render_template('analisar_desempenho.html', plot_url=plot_url, alunos_data=alunos_data)



