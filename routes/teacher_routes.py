from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from models import get_db, find_user_by_id, criar_aula
from utils import generate_plot
import sqlite3
import os
from werkzeug.utils import secure_filename

teacher_bp = Blueprint('teacher', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}  # Extensões permitidas
UPLOAD_FOLDER = os.path.join('static', 'uploads')

# Função para verificar se a extensão do arquivo é permitida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Garantir que a pasta de uploads existe
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
        return redirect(url_for('auth.login'))  # Redireciona para o login se o usuário não for professor

    if request.method == "POST":
        titulo = request.form.get("titulo")
        descricao = request.form.get("descricao")
        topico = request.form.get("topico")
        user_id = session.get('user')  # Adiciona o tópico da aula

        # Verifica se os campos obrigatórios foram preenchidos
        if not titulo or not descricao or not topico:
            flash("Todos os campos são obrigatórios", "error")
            return redirect(url_for('teacher.criarAula'))
        
        # Processa o arquivo enviado
        conteudo_file = request.files.get('file')
        if conteudo_file and allowed_file(conteudo_file.filename):
            print(f"Arquivo recebido: {conteudo_file.filename}")
            try:
                # Cria um nome seguro para o arquivo
                filename = secure_filename(conteudo_file.filename)
                # Define o caminho completo para salvar o arquivo dentro de 'static/uploads'
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                # Salva o arquivo na pasta 'static/uploads'
                conteudo_file.save(filepath)
                # Aqui, você pode salvar o nome do arquivo ou o caminho no banco de dados
                conteudo_nome = filename
            except Exception as e:
                print('erro')
                return redirect(url_for('teacher.criarAula'))
        else:
            print("Formato de arquivo inválido ou nenhum arquivo foi enviado.", "error")
            return redirect(url_for('teacher.criarAula'))

        try:
            # Função criar_aula com o novo caminho para o arquivo
            criar_aula(user_id, titulo, descricao, conteudo_nome, topico, filepath)
            flash("Aula criada com sucesso!", "success")
            return redirect(url_for('teacher.dashboard_professor'))  # Redireciona para o dashboard do professor
        except sqlite3.Error as e:
            flash(f"Erro ao criar a aula: {e}", "error")
            return redirect(url_for('teacher.criarAula'))

    return render_template("criarAula.html")

# Nova rota para ver os feedbacks
@teacher_bp.route('/dashboard_professor/feedbacks')
def ver_feedbacks():
    if 'user' in session and session['tipo'] == 'professor':
        db = get_db()
        respostas = db.execute(''' 
            SELECT usuarios.nome, respostas.section, respostas.response
            FROM respostas 
            JOIN usuarios ON respostas.user_id = usuarios.id
        ''').fetchall()
        
        # Organiza as respostas por aluno
        respostas_por_aluno = {}
        for resposta in respostas:
            nome = resposta['nome']
            if nome not in respostas_por_aluno:
                respostas_por_aluno[nome] = 0
            respostas_por_aluno[nome] += 1
        
        # Gera o gráfico com base nas respostas por aluno
        plot_respostas_url = generate_plot(respostas_por_aluno, 'Quantidade de Respostas por Aluno', 'Alunos', 'Respostas')

        return render_template('feedbacks_professor.html', plot_respostas_url=plot_respostas_url)
    
    return redirect(url_for('auth.login'))
