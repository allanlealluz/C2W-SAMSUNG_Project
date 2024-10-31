from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
import os
import numpy as np
from werkzeug.utils import secure_filename
from models import (
    find_user_by_id, criar_aula, get_aulas_by_professor,
    get_respostas_by_aula, get_progresso_by_aula, get_alunos,
    Adicionar_nota, resp_aluno, update_nota_resposta, get_student_scores,get_student_scores_topic
)
from utils import (
    generate_performance_plot, kmeans_clustering,
    generate_cluster_plot, generate_student_performance_plot,
    prever_notas,generate_performance_by_topic_plot
)
from sklearn.cluster import KMeans
import sqlite3
from collections import defaultdict

teacher_bp = Blueprint('teacher', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}
UPLOAD_FOLDER = "mysite/static/uploads"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@teacher_bp.route('/dashboard_professor')
def dashboard_professor():
    user_id = session.get("user")
    if user_id and session['tipo'] == 'professor':
        userData = find_user_by_id(user_id)


        alunos_data = get_student_scores()
        alunos_dict = {}

        for aluno_id, nome, nota, titulo, concluida in alunos_data:
            if nome not in alunos_dict:
                alunos_dict[nome] = {'total_notas': 0, 'num_notas': 0}
            if nota is not None:
                alunos_dict[nome]['total_notas'] += nota
                alunos_dict[nome]['num_notas'] += 1
            else:
                alunos_dict[nome]['total_notas'] = 0
                alunos_dict[nome]['num_notas'] = 0
        alunos_media = []
        for nome, data in alunos_dict.items():
            if data['num_notas'] == 0:
                alunos_media.append({'nome': nome, 'media': 0})
            else:
                media = data['total_notas'] / data['num_notas']
                alunos_media.append({'nome': nome, 'media': media})

        # Ordena alunos com base na média
        alunos_media = sorted(alunos_media, key=lambda x: x['media'] if isinstance(x['media'], float) else 0, reverse=True)

        return render_template(
            'dashboard_professor.html',
            user=userData,
            alunos=alunos_media
        )

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
            print("Todos os campos são obrigatórios", "error")
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
                print('Erro ao salvar o arquivo: {}'.format(e), 'error')
                return redirect(url_for('teacher.criarAula'))

        if conteudo_nome is None and not request.form.get("conteudo"):
            print("Você deve enviar um arquivo ou fornecer o conteúdo da aula.", "error")
            return redirect(url_for('teacher.criarAula'))

        conteudo = request.form.get("conteudo") if conteudo_nome is None else conteudo_nome

        try:
            criar_aula(user_id, titulo, descricao, conteudo, perguntas, topico, conteudo_nome)
            print("Aula criada com sucesso!", "success")
            return redirect(url_for('teacher.dashboard_professor'))
        except sqlite3.Error as e:
            print(f"Erro ao criar a aula: {e}", "error")
            return redirect(url_for('teacher.criarAula'))

    return render_template("criarAula.html")
@teacher_bp.route('/dashboard_professor/feedbacks')
def ver_feedbacks():
    if session.get('user') and session.get('tipo') == 'professor':
        user_id = session.get('user')

        feedbacks = {}
        progresso_por_aluno = {}
        total_alunos = set()
        notas_por_topico = defaultdict(list)
        notas_por_aula = defaultdict(list)
        alunos_scores = get_student_scores()
        plot_url = None
        previsoes = {}
        print("Start processing feedbacks")

        try:
            aulas = get_aulas_by_professor(user_id)
            print(f"Aulas encontradas: {aulas}")
            if not aulas:
                print("Nenhuma aula encontrada para o professor.")
                return redirect(url_for('teacher.dashboard_professor'))

            for aula in aulas:
                aula_id = aula[0]
                titulo_aula = aula[2]
                print(f"Processing aula_id: {aula_id}, titulo: {titulo_aula}")

                respostas = get_respostas_by_aula(aula_id)
                print(f"Respostas para aula {aula_id} ({titulo_aula}): {respostas}")

                if respostas is None:
                    print(f"Erro ao buscar respostas para a aula {titulo_aula}.")
                    continue

                feedbacks[titulo_aula] = respostas if respostas else []
                progresso = get_progresso_by_aula(aula_id)
                print(f"Progresso para aula {aula_id}: {progresso}")

                if progresso is None:
                    print(f"Erro ao buscar progresso para a aula {titulo_aula}.")
                    continue

                for aluno in progresso:
                    nome = aluno['nome']
                    total_alunos.add(nome)
                    progresso_por_aluno[nome] = aluno['concluida']
                for resposta in respostas:
                    aluno_id = resposta['user_id']
                    nota = resposta['nota'] if 'nota' in resposta else 0
                    topico = resposta['topico'] if 'topico' in resposta else "Robótica"

                    if isinstance(nota, (int, float)):
                        notas_por_aula[aula_id].append(nota)
                        if topico:
                            notas_por_topico[topico].append(nota)


            medias_por_aula = {aula_id: (sum(notas) / len(notas)) if notas else 0
                               for aula_id, notas in notas_por_aula.items()}
            medias_por_topico = {topico: (sum(notas) / len(notas)) if notas else 0
                                 for topico, notas in notas_por_topico.items()}

            alunos_data = {}
            for aluno_id, nome, nota, progresso, aula in alunos_scores:
                if nome not in alunos_data:
                    alunos_data[nome] = {'historico': [], 'id': aluno_id}
                alunos_data[nome]['historico'].append({
                    'nota': nota,
                    'progresso': progresso,
                    'aula': aula
                })

            notas = np.array([entry['nota'] for aluno in alunos_data.values() for entry in aluno['historico']])
            progresso = np.array([entry['progresso'] for aluno in alunos_data.values() for entry in aluno['historico']])

            if len(notas) > 0:
                kmeans = KMeans(n_clusters=3)
                X = np.column_stack((notas, progresso))
                kmeans.fit(X)
                labels = kmeans.labels_

                grupos_alunos = {i: [] for i in range(3)}

                for i, aluno in enumerate(alunos_data.keys()):
                    grupos_alunos[labels[i]].append(aluno)

                print("Grupos de alunos:", grupos_alunos)

                previsoes = prever_notas(alunos_data)
                print("Previsões:", previsoes)

                for nome, dados in previsoes.items():
                    notas_historico = [entry['nota'] for entry in alunos_data[nome]['historico']]
                    classificacao = classificar_aluno(notas_historico)
                    previsoes[nome]['classificacao'] = classificacao

                if alunos_data:
                    plot_url = generate_performance_plot(alunos_data, previsoes)
                    print("URL do gráfico:", plot_url)

            return render_template(
                'feedbacks_professor.html',
                feedbacks=feedbacks,
                plot_respostas_url=plot_url,
                previsoes=previsoes,
                progresso=progresso_por_aluno,
                medias_por_aula=medias_por_aula,
                medias_por_topico=medias_por_topico,
                total_alunos=len(total_alunos),
                grupos=grupos_alunos
            )
        except Exception as e:
            print(f"Erro ao carregar feedbacks: {e}")
            return render_template(
                'feedbacks_professor.html',
                feedbacks=feedbacks,
                plot_respostas_url=plot_url,
                previsoes=previsoes,
                progresso=progresso_por_aluno,
                medias_por_aula={},
                medias_por_topico={},
                total_alunos=len(total_alunos),
                grupos={}
            )
    return redirect(url_for('auth.login'))

def classificar_aluno(notas):
    media_nota = np.mean(notas) if notas else 0
    if media_nota < 5:
        return "Baixas Notas"
    elif 5 <= media_nota < 7:
        return "Notas Médias"
    else:
        return "Altas Notas"

@teacher_bp.route('/dashboard_professor/avaliar_alunos', methods=["GET"])
def avaliar_alunos():
    if 'user' not in session or session['tipo'] != 'professor':
        return redirect(url_for('auth.login'))

    try:
        alunos = get_alunos()
        return render_template('avaliar_alunos.html', alunos=alunos)
    except Exception as e:
        print(f"Erro ao obter alunos: {e}", "error")
        return redirect(url_for('teacher.dashboard_professor'))


@teacher_bp.route('/dashboard_professor/analisar_aluno/<int:aluno_id>', methods=["GET", "POST"])
def analisar_aluno(aluno_id):
    if 'user' not in session or session['tipo'] != 'professor':
        return redirect(url_for('auth.login'))

    if request.method == "POST":
        nota = request.form.get('nota')
        if nota:
            try:
                Adicionar_nota(1, aluno_id, nota)
                print("Nota adicionada com sucesso!", "success")
            except Exception as e:
                print(f"Erro ao adicionar nota: {e}", "error")
            return redirect(url_for('teacher.avaliar_alunos'))

    try:
        resposta = [resp for resp in resp_aluno(aluno_id) if resp["nota"] is None]
        return render_template('analisar_aluno.html', resposta=resposta, aluno_id=aluno_id)
    except Exception as e:
        print(f"Erro ao analisar aluno: {e}", "error")
        return redirect(url_for('teacher.avaliar_alunos'))


@teacher_bp.route('/dashboard_professor/update_nota_resposta', methods=["GET", "POST"])
def update_nota_resposta_route():
    data = request.get_json()
    resposta_id = data.get("resposta_id")
    nota = data.get("nota")

    if resposta_id and nota is not None:
        try:
            update_nota_resposta(resposta_id, nota)
            return jsonify({"success": True}), 200
        except Exception as e:
            return jsonify({"error": f"Erro ao atualizar nota: {e}"}), 500

    return jsonify({"error": "Dados inválidos"}), 400


@teacher_bp.route('/dashboard_professor/analisar_desempenho', methods=["GET"])
def analisar_desempenho():
    if 'user' not in session or session['tipo'] != 'professor':
        return redirect(url_for('auth.login'))

    try:
        alunos_data = get_student_scores_topic()

        if not alunos_data:
            print("Nenhum dado disponível para análise.", "error")
            return redirect(url_for('teacher.dashboard_professor'))

        performance_by_topic_plot_url = generate_performance_by_topic_plot(alunos_data)

        X, labels, centroids = kmeans_clustering(alunos_data)

        if X is None or labels is None or centroids is None:
            print("Erro ao realizar clustering. Verifique os dados.", "error")
            return redirect(url_for('teacher.dashboard_professor'))

        plot_url = generate_cluster_plot(X, labels, centroids, alunos_data)
        student_performance_plot_url = generate_student_performance_plot(alunos_data)

        return render_template('analisar_desempenho.html',
                               plot_url=plot_url,
                               student_performance_plot_url=student_performance_plot_url,
                               performance_by_topic_plot_url=performance_by_topic_plot_url,
                               alunos_data=alunos_data)

    except Exception as e:
        print(f"Erro ao analisar desempenho: {e}", "error")
        return redirect(url_for('teacher.dashboard_professor'))




