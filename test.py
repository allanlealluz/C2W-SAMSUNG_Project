from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

DATABASE = 'database.db'

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.route("/")
def index():
    return render_template("home.html")

@app.route("/initdb")
def initiate_database():
    init_db()
    return "DATABASE CONNECTED"

@app.route("/cadastro", methods=["POST", "GET"])
def cadastro():
    if request.method == "POST":
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']

        db = get_db()
        db.execute('INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)', (nome, email, senha))
        db.commit()

        return jsonify({"message": "Usuario cadastrado com sucesso!"})

    return render_template("cadastro.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form['email']
        senha = request.form['senha']

        db = get_db()
        user = db.execute('SELECT * FROM usuarios WHERE email = ?', (email,)).fetchone()

        if user and check_password_hash(user['senha'], senha):
            return jsonify({"message": "Login bem-sucedido!"})
        else:
            return jsonify({"message": "Credenciais inválidas!"})

    return render_template("login.html")

if __name__ == "__main__":
    app.run(debug=True)
