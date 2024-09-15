from flask import Flask, render_template, request, jsonify, session, url_for, redirect
import sqlite3
from hashlib import sha256

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
            session["user"] = email
            session["tipo"] = user['tipo']  # Salvando o tipo de usuário na sessão
            if user['tipo'] == 'professor':
                return redirect(url_for('dashboard_professor'))
            else:
                return redirect(url_for('dashboard_aluno'))
        else:
            return jsonify({"message": "Credenciais inválidas!"})
    return render_template("login.html")
@app.route("/robotica")
def robotica():
    return render_template("robotica.html")
@app.route("/example")
def example():
    return render_template("exampleFetch.html")
@app.route('/submit_data', methods=['POST', "GET"])
def submit_data():
    # Pegar os dados enviados no JSON
    data = request.get_json()
    # Processar os dados (por exemplo, imprimir no console)
    print("Dados recebidos:", data)
    # Você pode processar e armazenar esses dados no banco, se necessário
    # Retornar uma resposta JSON para o cliente
    return jsonify({"message": "Dados recebidos com sucesso!"}), 200
@app.route('/submit_response', methods=['POST'])
def submit_response():
    if 'user' not in session:
        return jsonify({"message": "Usuário não autenticado!"}), 401
    data = request.get_json()
    user_response = data['response']
    section = data['section']
    
    user_id = session['user']

    db = get_db()
    db.execute('INSERT INTO respostas (user_id, section, response) VALUES (?, ?, ?)', 
               (user_id, section, user_response))
    db.commit()

    return jsonify({"message": "Resposta enviada com sucesso!"})
@app.route('/main')
@app.route('/dashboard_aluno')
def dashboard_aluno():
    if 'user' in session and session['tipo'] == 'aluno':
        return render_template('dashboard_aluno.html', user=session['user'])
    return redirect(url_for('login'))

@app.route('/dashboard_professor')
def dashboard_professor():
    if 'user' in session and session['tipo'] == 'professor':
        return render_template('dashboard_professor.html', user=session['user'])
    return redirect(url_for('login'))
if __name__ == "__main__":
    app.run(debug=True)
