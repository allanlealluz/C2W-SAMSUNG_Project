from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from models import get_db, find_user_by_id, criar_aula
from utils import generate_plot
import sqlite3
import os
from werkzeug.utils import secure_filename
from sklearn.cluster import KMeans
import numpy as np
import matplotlib.pyplot as plt

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
        user_id = session.get('user')  # ID do professor logado

        # Busca todas as aulas do professor
        aulas = db.execute('''
            SELECT id, titulo FROM aulas WHERE professor_id = ?
        ''', (user_id,)).fetchall()

        feedbacks = {}
        progresso_por_aluno = {}
        palavras_chave = {}
        total_alunos = set()  # Conjunto para contar alunos únicos

        for aula in aulas:
            aula_id = aula['id']
            titulo_aula = aula['titulo']
            
            # Consulta para buscar as respostas dos alunos para esta aula específica
            respostas = db.execute('''
                SELECT usuarios.nome, respostas.pergunta_id, respostas.resposta, perguntas.texto AS pergunta_texto
                FROM respostas
                JOIN usuarios ON respostas.user_id = usuarios.id
                JOIN perguntas ON respostas.pergunta_id = perguntas.id
                WHERE respostas.aula_id = ?
            ''', (aula_id,)).fetchall()

            feedbacks[titulo_aula] = respostas

            # Extrai palavras-chave das perguntas
            for resposta in respostas:
                nome_aluno = resposta['nome']
                pergunta_texto = resposta['pergunta_texto']
                
                # Extraindo palavras-chave (exemplo simples, idealmente usar NLP)
                keywords = pergunta_texto.split()[:3]  # Aqui pegamos as 3 primeiras palavras como exemplo

                if nome_aluno not in palavras_chave:
                    palavras_chave[nome_aluno] = []
                palavras_chave[nome_aluno].extend(keywords)

            # Busca progresso dos alunos por aula
            progresso = db.execute('''
                SELECT usuarios.nome, progresso_aulas.concluida
                FROM progresso_aulas
                JOIN usuarios ON progresso_aulas.user_id = usuarios.id
                WHERE progresso_aulas.aula_id = ?
            ''', (aula_id,)).fetchall()

            # Agregando progresso dos alunos
            for aluno in progresso:
                nome = aluno['nome']
                total_alunos.add(nome)  # Adiciona ao conjunto de alunos únicos

                if nome not in progresso_por_aluno:
                    progresso_por_aluno[nome] = []
                progresso_por_aluno[nome].append(aluno['concluida'])

        # Preparando dados para clustering
        alunos_data = {}
        for nome, progresso_list in progresso_por_aluno.items():
            progresso_medio = np.mean(progresso_list) * 100  # Progresso médio em %
            feedback_count = sum(1 for feedback_list in feedbacks.values() for f in feedback_list if f['nome'] == nome)
            alunos_data[nome] = [progresso_medio, feedback_count]

        # Garantindo que temos alunos suficientes para rodar o KMeans
        if len(alunos_data) >= 3:
            X = np.array([data for data in alunos_data.values()])
            nomes_alunos = list(alunos_data.keys())

            # Aplicando K-Means para encontrar perfis de alunos
            kmeans = KMeans(n_clusters=3, random_state=42)
            labels = kmeans.fit_predict(X)

            # Visualizando os resultados
            plt.figure(figsize=(10, 6))
            scatter = plt.scatter(X[:, 0], X[:, 1], c=labels, cmap='viridis', marker='o', edgecolor='k', s=100)

            # Adicionando centróides
            centroids = kmeans.cluster_centers_
            plt.scatter(centroids[:, 0], centroids[:, 1], c='red', marker='X', s=200, label='Centroides')

            # Anotando os alunos
            for i, nome in enumerate(nomes_alunos):
                plt.annotate(nome, (X[i, 0], X[i, 1]), fontsize=9, ha='right')

            plt.title('Perfis de Alunos Baseados em Progresso e Feedbacks')
            plt.xlabel('Progresso Médio (%)')
            plt.ylabel('Quantidade de Feedbacks')
            plt.grid()
            plt.legend()

            # Caminho para salvar o gráfico
            img_dir = os.path.join(os.getcwd(), 'static', 'images')
            os.makedirs(img_dir, exist_ok=True)  # Cria o diretório se não existir

            plot_url = os.path.join(img_dir, 'cluster_plot.png')
            plt.savefig(plot_url)
            plt.close()

            # Identificando alunos com progresso abaixo da média
            progresso_medio_total = np.mean([data[0] for data in alunos_data.values()])
            alunos_abaixo_da_media = {nome: progresso_por_aluno[nome] for nome, data in alunos_data.items() if data[0] < progresso_medio_total}

            # Relacionando palavras-chave para alunos abaixo da média
            dificuldades = {nome: palavras_chave.get(nome, []) for nome in alunos_abaixo_da_media}

            return render_template(
                'feedbacks_professor.html',
                feedbacks=feedbacks,
                dificuldades=dificuldades,
                plot_respostas_url='/static/images/cluster_plot.png',
                progresso=progresso_por_aluno  # Passando a variável progresso para o template
            )

        else:
            # Caso não tenha alunos suficientes, uma mensagem de aviso
            return render_template(
                'feedbacks_professor.html',
                feedbacks=feedbacks,
                mensagem='Não há dados suficientes para gerar clusters de alunos.',
                progresso=progresso_por_aluno  # Passando a variável progresso para o template
            )

    return redirect(url_for('auth.login'))
