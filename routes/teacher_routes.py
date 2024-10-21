from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from models import get_db, find_user_by_id, criar_aula
from utils import generate_plot
import sqlite3
import os
from werkzeug.utils import secure_filename

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
        aulas = db.execute('''
            SELECT id, titulo FROM aulas WHERE professor_id = ?
        ''', (user_id,)).fetchall()
         for aula in aulas:
            aula_id = aula['id']
            titulo_aula = aula['titulo']
            respostas = db.execute('''
                SELECT usuarios.nome, respostas.aula_id, perguntas.texto AS pergunta, respostas.resposta
                FROM respostas
                WHERE respostas.aula_id = ?
            ''', (aula_id,)).fetchall()

            feedbacks[titulo_aula] = respostas

            progresso_aula = db.execute('''
                SELECT usuarios.nome, COUNT(progresso_atividades.section_id) as secoes_completadas, 
                (COUNT(progresso_atividades.section_id) * 100.0 / (SELECT COUNT(id) FROM perguntas WHERE aula_id = ?)) as progresso
                FROM progresso_atividades
                JOIN usuarios ON progresso_atividades.user_id = usuarios.id
                WHERE progresso_atividades.aula_id = ? AND progresso_atividades.completou = 1
                GROUP BY usuarios.nome
            ''', (aula_id, aula_id)).fetchall()

            # Armazena o progresso no dicionário progresso
            progresso[titulo_aula] = progresso_aula

        # Gera os gráficos por aula com base no número de respostas
        respostas_por_aula = {aula['titulo']: len(feedbacks[aula['titulo']]) for aula in aulas}
        plot_respostas_url = generate_plot(respostas_por_aula, 'Quantidade de Respostas por Aula', 'Aulas', 'Respostas')

        # Gera gráfico de progresso dos alunos
        progresso_por_aula = {aula['titulo']: sum([aluno['progresso'] for aluno in progresso[aula['titulo']]]) / len(progresso[aula['titulo']]) if progresso[aula['titulo']] else 0 for aula in aulas}
        plot_progresso_url = generate_plot(progresso_por_aula, 'Progresso Médio por Aula', 'Aulas', 'Progresso (%)')

        return render_template('feedbacks_professor.html', feedbacks=feedbacks, progresso=progresso, plot_respostas_url=plot_respostas_url, plot_progresso_url=plot_progresso_url)

    return redirect(url_for('auth.login'))
