from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from models import get_db, find_user_by_id, criar_aula
from utils import generate_plot
import sqlite3
import os
from werkzeug.utils import secure_filename

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
        
        # Obtemos a quantidade de atividades completadas por cada aluno a partir de progresso_atividades
        respostas = db.execute('''
            SELECT usuarios.nome, COUNT(progresso_atividades.section_id) AS total_respostas
            FROM progresso_atividades
            JOIN usuarios ON progresso_atividades.user_id = usuarios.id
            WHERE progresso_atividades.completou = 1
            GROUP BY usuarios.nome
        ''').fetchall()
        
        # Agora, organizamos os dados para o gráfico
        respostas_por_aluno = {}
        for resposta in respostas:
            nome = resposta['nome']
            total_respostas = resposta['total_respostas']
            respostas_por_aluno[nome] = total_respostas
        
        # Geramos o gráfico com base nos dados obtidos
        plot_respostas_url = generate_plot(
            respostas_por_aluno, 
            'Quantidade de Atividades Completadas por Aluno', 
            'Alunos', 
            'Atividades Completadas'
        )

        return render_template('feedbacks_professor.html', plot_respostas_url=plot_respostas_url)
    
    return redirect(url_for('auth.login'))

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}  # Extensões permitidas
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
UPLOAD_FOLDER = os.path.join('static', 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
@teacher_bp.route('/Criar_Aula', methods=["GET", "POST"])
def criarAula():
    if 'user' not in session or session['tipo'] != 'professor':
        return redirect(url_for('auth.login'))  # Redireciona para o login se o usuário não for professor

    if request.method == "POST":
        titulo = request.form.get("titulo")
        conteudo_nome = request.form.get("conteudo_nome")  # Obtenha o nome do conteúdo (se houver)
        descricao = request.form.get("descricao")
        topico = request.form.get("topico")
        user_id = session.get('user')  # Adiciona o tópico da aula

        if not titulo or not descricao or not topico:
            flash("Todos os campos são obrigatórios", "error")
            return redirect(url_for('teacher.criarAula'))
        
        # Processa o arquivo enviado
        conteudo_file = request.files.get('conteudo_file')
        if conteudo_file and allowed_file(conteudo_file.filename):
            # Cria um nome seguro para o arquivo
            filename = secure_filename(conteudo_file.filename)
            # Define o caminho completo para salvar o arquivo dentro de 'static/uploads'
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            # Salva o arquivo na pasta 'static/uploads'
            conteudo_file.save(filepath)
            # Aqui, você pode salvar o caminho do arquivo no banco de dados se necessário
            conteudo_nome = filename
        else:
            flash("Formato de arquivo inválido ou nenhum arquivo foi enviado.", "error")
            print("dale")
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
