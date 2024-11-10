from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify, flash
import os
import numpy as np
from werkzeug.utils import secure_filename
from models import (
    find_user_by_id, criar_aula, get_cursos,get_modulos_by_curso_id,
    get_respostas_by_aula, get_progresso_by_aula, get_alunos,
    Adicionar_nota, resp_aluno, update_nota_resposta, get_student_scores,get_db, criar_modulos, get_aulas_por_modulo, get_student_scores_by_module
)
from utils import (
    generate_performance_plot, kmeans_clustering,
    generate_cluster_plot, generate_student_performance_plot,
    prever_notas, generate_performance_by_module_plot
)
from sklearn.cluster import KMeans
import sqlite3
from collections import defaultdict
import os

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
        modulo_id = request.form.get("modulo_id")
        curso_id = request.form.get("curso_id")  # Curso selecionado

        conteudo = request.form.get("conteudo")
        perguntas = request.form.getlist("perguntas[]")
        conteudo_nome = None
        conteudo_file = request.files.get('file')

        if conteudo_file and allowed_file(conteudo_file.filename):
            try:
                filename = secure_filename(conteudo_file.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                conteudo_file.save(filepath)
                conteudo_nome = filename
            except Exception as e:
                print(f"Erro ao salvar o arquivo: {e}", "error")
                return redirect(url_for('teacher.criar_aula'))

        # Verifica se todos os campos obrigatórios foram preenchidos
        if not titulo or not descricao or not modulo_id or not curso_id:
            print("Todos os campos são obrigatórios", "error")
            return redirect(url_for('teacher.criar_aula'))

        conteudo = conteudo or conteudo_nome

        # Cria a aula
        try:
            criar_aula(modulo_id,curso_id, titulo, descricao, conteudo, perguntas, conteudo_nome)
            print("Aula criada com sucesso!", "success")
            return redirect(url_for('teacher.dashboard_professor'))
        except sqlite3.Error as e:
            print(f"Erro ao criar a aula: {e}", "error")
            return redirect(url_for('teacher.criar_aula'))

    # Carregar os cursos do professor
    cursos = get_cursos()  # Função que retorna os cursos do professor

    return render_template("criarAula.html", cursos=cursos)
@teacher_bp.route('/api/get_modulos/<int:curso_id>', methods=["GET"])
def get_modulos(curso_id):
    db = get_db()
    
    # Executa a consulta para obter os módulos do curso
    modulos = db.execute('''
        SELECT id, titulo
        FROM modulos
        WHERE curso_id = ?
    ''', (curso_id,)).fetchall()

    modulos_list = [{'id': modulo['id'], 'titulo': modulo['titulo']} for modulo in modulos]

    return jsonify({'modulos': modulos_list})
@teacher_bp.route('/criar_modulo', methods=["GET", "POST"])
def criar_modulo():
    user_id = session.get("user")
    if 'user' not in session or session['tipo'] != 'professor':
        return redirect(url_for('auth.login'))

    if request.method == "POST":
        titulo = request.form.get("titulo")
        descricao = request.form.get("descricao")
        curso_id = request.form.get("curso_id")
        if not titulo or not descricao or not curso_id:
            flash("Todos os campos são obrigatórios", "error")
            return redirect(url_for('teacher.criar_modulo'))
        try:
            criar_modulos(curso_id, titulo, descricao,user_id)
            flash("Módulo criado com sucesso!", "success")
            return redirect(url_for('teacher.dashboard_professor'))
        except sqlite3.Error as e:
            flash(f"Erro ao criar o módulo: {e}", "error")
            return redirect(url_for('teacher.criar_modulo'))

    cursos = get_cursos()
    return render_template("criar_modulo.html", cursos=cursos)
@teacher_bp.route('/dashboard_professor/feedbacks')
def ver_feedbacks():
    if session.get('user') and session.get('tipo') == 'professor':
        user_id = session.get('user')
        feedbacks = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        progresso_por_aluno = {}
        total_alunos = set()
        notas_por_curso = defaultdict(lambda: defaultdict(list))
        notas_por_aula = defaultdict(list)
        alunos_scores = get_student_scores()
        plot_url = None
        previsoes = {}
        medias_por_curso = {}
        medias_por_aula = {}
        feedback_texto = ['']

        try:
            cursos = get_cursos()
            if not cursos:
                return redirect(url_for('teacher.dashboard_professor'))

            for curso in cursos:
                curso_id, curso_nome = curso[:2]
                modulos = get_modulos_by_curso_id(curso_id)
                medias_por_curso[curso_nome] = {}

                for modulo in modulos:
                    modulo_id, modulo_nome = modulo[0], modulo[1]
                    medias_por_curso[curso_nome][modulo_nome] = {}

                    aulas = get_aulas_por_modulo(modulo_id)

                    aulas_processadas = set() 
                    for aula in aulas:
                        aula_id, titulo_aula = aula[0], aula[3]
                        if aula_id in aulas_processadas:
                            continue
                        aulas_processadas.add(aula_id)
                        respostas = get_respostas_by_aula(aula_id)
                        feedbacks[curso_nome][modulo_nome][titulo_aula] = respostas if respostas else []
                        progresso = get_progresso_by_aula(aula_id)
                        for aluno in progresso:
                            nome = aluno['nome']
                            total_alunos.add(nome)
                            progresso_por_aluno[nome] = aluno['concluida']
                        for resposta in respostas:
                            aluno_id = resposta['user_id']
                            nota = resposta['nota']
                            if isinstance(nota, (int, float)):
                                notas_por_aula[aula_id].append(nota)
                                notas_por_curso[curso_nome][modulo_nome].append(nota)

            medias_por_aula = {titulo_aula: (sum(notas) / len(notas)) if notas else 0 for aula_id, notas in notas_por_aula.items()}
            medias_por_curso = {
                curso: {modulo: (sum(notas) / len(notas)) if notas else 0 for modulo, notas in modulos.items()}
                for curso, modulos in notas_por_curso.items()
            }

            alunos_data = defaultdict(lambda: {'historico': [], 'id': None})
            for aluno_id, nome, nota, progresso, aula in alunos_scores:
                if alunos_data[nome]['id'] is None:
                    alunos_data[nome]['id'] = aluno_id
                alunos_data[nome]['historico'].append({'nota': nota, 'progresso': progresso, 'aula': aula})

            if alunos_data:
                previsoes = prever_notas(alunos_data)
                for nome, dados in previsoes.items():
                    notas_historico = [entry['nota'] for entry in alunos_data[nome]['historico']]
                    previsoes[nome]['classificacao'] = classificar_aluno(notas_historico)
                plot_url = generate_performance_plot(alunos_data, previsoes)
                
            feedback_texto = gerar_feedback_textual(medias_por_aula, medias_por_curso, previsoes, progresso_por_aluno)

            return render_template(
                'feedbacks_professor.html',
                feedbacks=dict(feedbacks),
                plot_respostas_url=plot_url,
                previsoes=previsoes,
                total_alunos=len(total_alunos),
                feedback_texto=feedback_texto,
                medias_por_aula=medias_por_aula,
                medias_por_curso=medias_por_curso
            )

        except Exception as e:
            print(f"Erro ao carregar feedbacks: {e}")
            return render_template(
                'feedbacks_professor.html',
                feedbacks=dict(feedbacks),
                plot_respostas_url=plot_url,
                previsoes=previsoes,
                total_alunos=len(total_alunos),
                feedback_texto=feedback_texto,
                medias_por_aula=medias_por_aula,
                medias_por_curso=medias_por_curso
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
def gerar_feedback_textual(medias_por_aula, medias_por_topico, previsoes, progresso_por_aluno):
    feedback = []

    try:
        if medias_por_aula:
            feedback.append("Médias por Aula:")
            for aula, media in medias_por_aula.items():
                if isinstance(media, (int, float)):
                    feedback.append(f"Aula {aula}: Média {media:.2f}")
                else:
                    feedback.append(f"Aula {aula}: Média inválida")

        if medias_por_topico:
            feedback.append("\nMédias por Tópico:")
            for topico, media in medias_por_topico.items():
                if isinstance(media, (int, float)):
                    feedback.append(f"Tópico {topico}: Média {media:.2f}")
                else:
                    feedback.append(f"Tópico {topico}: Média inválida")

        if previsoes:
            print(previsoes) 
            feedback.append("\nPrevisões:")
            for aluno, dados in previsoes.items():
                nota_arredondada = round(dados.get('proxima_nota', 0), 2)
                feedback.append(f"Aluno {aluno}: Previsão {nota_arredondada}")

        if progresso_por_aluno:
            feedback.append("\nProgresso por Aluno:")
            for aluno, progresso in progresso_por_aluno.items():
                feedback.append(f"Aluno {aluno}: Progresso {progresso}")

        return feedback

    except Exception as e:
        print(f"Erro ao gerar feedback textual: {e}")
        return ["Erro ao gerar feedback textual."]
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
        alunos_data = get_student_scores_by_module()
        if not alunos_data:
            print("Nenhum dado disponível para análise.", "error")
            return redirect(url_for('teacher.dashboard_professor'))
        performance_by_topic_plot_url = generate_performance_by_module_plot(alunos_data)
        print("por enquanto ok")
        X, labels, centroids = kmeans_clustering(alunos_data)

        if X is None or labels is None or centroids is None:
            print("Erro ao realizar clustering. Verifique os dados.", "error")
            return redirect(url_for('teacher.dashboard_professor'))
        print("por enquanto ok")
        plot_url = generate_cluster_plot(X, labels, centroids, alunos_data)
        student_performance_plot_url = generate_student_performance_plot(alunos_data)
        print("por enquanto ok")
        return render_template('analisar_desempenho.html',
                               plot_url=plot_url,
                               student_performance_plot_url=student_performance_plot_url,
                               performance_by_topic_plot_url=performance_by_topic_plot_url,
                               alunos_data=alunos_data)

    except Exception as e:
        print(f"Erro ao analisar desempenho: {e}", "error")
        return redirect(url_for('teacher.dashboard_professor'))


