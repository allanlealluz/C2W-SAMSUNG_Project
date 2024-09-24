from flask import Flask, render_template, request, jsonify, session, url_for, redirect
import sqlite3
from hashlib import sha256
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)
app.secret_key = "aaaa"
## Definir database
DATABASE = 'database.db'
# Conectar com a base de dados sqlite
def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db
#chama a função getdb e cria a tabela
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()
#main page
@app.route("/")
def index():
    init_db()
    return render_template("home.html")
#chama a init_db através da url
@app.route("/initdb")
def initiate_database():
    init_db()
    return "DATABASE CONNECTED"
#pagina de cadastro
# Página de cadastro
@app.route("/cadastro", methods=["POST", "GET"])
def cadastro():
    if request.method == "POST":
        nome = request.form['nome']
        email = request.form['email']
        senha = sha256(request.form['senha'].encode('utf-8')).hexdigest()
        tipo = request.form['tipo']  # Novo campo para o tipo de usuário

        db = get_db()
        db.execute('INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)', (nome, email, senha, tipo))
        db.commit()
        return render_template("login.html")
    return render_template("cadastro.html")
#pagina de login
@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form['email']
        senha = sha256(request.form['senha'].encode('utf-8')).hexdigest()
        db = get_db()
        user = db.execute('SELECT * FROM usuarios WHERE email = ?', (email,)).fetchone()
        if user and user['senha'] == senha:
            session["user"] = user['id']
            session["tipo"] = user['tipo']  # Salvando o tipo de usuário na sessão
            if user['tipo'] == 'professor':
                return redirect(url_for('dashboard_professor'))
            else:
                return redirect(url_for('dashboard_aluno'))
        else:
            return jsonify({"message": "Credenciais inválidas!"})
    return render_template("login.html")
@app.route("/robotica")
def aula1():
    if 'user' in session and session['tipo'] == 'aluno':
        return render_template("aula1.html")
    return redirect(url_for('login'))
@app.route('/submit_response_text', methods=['POST'])
def submit_response_text():
    # Recebe a resposta do aluno em JSON
    
    data = request.get_json()
    user_response = data['response']
    section = data['section']
    
    # Captura o ID do usuário logado
    user_id = session['user']

    # Armazena a resposta no banco de dados
    db = get_db()
    db.execute("INSERT INTO respostas (user_id, section, response,aula_id) VALUES (?, ?, ?, 1)", 
               (user_id, section, user_response))
    
    db.commit()

    return jsonify({"message": "Resposta enviada com sucesso!"}), 200

@app.route('/update_progress', methods=['POST',"GET"])
def update_progress():
    # Recebe a seção que o aluno completou
    data = request.get_json()
    section = data['section']
    
    # Captura o ID do usuário logado
    user_id = session['user']

    # Atualiza o progresso do aluno no banco de dados
    db = get_db()
    db.execute('''
        INSERT INTO progresso_atividades (user_id, section_id, completou, aula_id)
        VALUES (?, ?, 1, 1)
        ON CONFLICT(user_id, section_id) DO UPDATE SET completou=1
    ''', (user_id, section))
    
    db.commit()

    return jsonify({"message": "Progresso atualizado com sucesso!"}), 200


@app.route('/main')
@app.route('/dashboard_aluno')
def dashboard_aluno():
    db = get_db()
    data = db.execute("SELECT nome FROM usuarios where id = ? ",(session['user'],)).fetchone()
    if 'user' in session and session['tipo'] == 'aluno':
        return render_template('dashboard_aluno.html', user=data)
    return redirect(url_for('login'))

@app.route('/dashboard_professor')
def dashboard_professor():
    db = get_db()
    data = db.execute("SELECT nome FROM usuarios where id = ? ",(session['user'],)).fetchone()
    if 'user' in session and session['tipo'] == 'professor':
        return render_template('dashboard_professor.html', user=data)
    return redirect(url_for('login'))
@app.route('/dashboard_professor/feedbacks')
def ver_feedbacks():
    if 'user' in session and session['tipo'] == 'professor':
        db = get_db()
        
        # Consultar as respostas dos alunos
        respostas = db.execute(''' 
            SELECT usuarios.nome, respostas.section, respostas.response
            FROM respostas 
            JOIN usuarios ON respostas.user_id = usuarios.id
        ''').fetchall()
        
        # Consultar o progresso dos alunos
        progresso = db.execute(''' 
            SELECT usuarios.nome, progresso_atividades.section_id, progresso_atividades.completou
            FROM progresso_atividades 
            JOIN usuarios ON progresso_atividades.user_id = usuarios.id
        ''').fetchall()
        
        # Gerar o gráfico de respostas dos alunos por seção
        fig, ax = plt.subplots()
        alunos = [resposta['nome'] for resposta in respostas]
        quantidade_respostas = [respostas.count(resposta) for resposta in alunos]
        
        ax.bar(alunos, quantidade_respostas, color='blue')
        ax.set_title('Quantidade de Respostas por Aluno')
        ax.set_xlabel('Alunos')
        ax.set_ylabel('Quantidade de Respostas')
        
        # Salvar o gráfico em uma imagem base64
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_respostas_url = base64.b64encode(img.getvalue()).decode()
        plt.close(fig)

        # Gerar outro gráfico para o progresso
        fig, ax = plt.subplots()
        alunos_progresso = [pro['nome'] for pro in progresso]
        progresso_alunos = [pro['completou'] for pro in progresso]
        
        ax.bar(alunos_progresso, progresso_alunos, color='green')
        ax.set_title('Progresso dos Alunos por Seção')
        ax.set_xlabel('Alunos')
        ax.set_ylabel('Seções Completas')
        
        # Salvar o gráfico em uma imagem base64
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_progresso_url = base64.b64encode(img.getvalue()).decode()
        plt.close(fig)

        return render_template('feedbacks_professor.html', respostas=respostas, progresso=progresso, plot_respostas_url=plot_respostas_url, plot_progresso_url=plot_progresso_url)
    
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
 