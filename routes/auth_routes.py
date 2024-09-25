# routes/auth_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, session
from models import create_user, find_user
from hashlib import sha256
from models import find_user,create_user,find_user_by_id
auth_bp = Blueprint('auth', __name__)
student_bp = Blueprint('student', __name__)

@auth_bp.route("/")
def index():
    return render_template("home.html")
@auth_bp.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form['email']
        senha = sha256(request.form['senha'].encode('utf-8')).hexdigest()
        user = find_user(email)
        if user and user['senha'] == senha:
            session["user"] = user['id']
            session["tipo"] = user['tipo']
            return redirect(url_for('teacher.dashboard_professor') if user['tipo'] == 'professor' else url_for('student.dashboard_aluno'))
        return {"message": "Credenciais inválidas!"}, 401
    return render_template("login.html")

@auth_bp.route("/cadastro", methods=["POST", "GET"])
def cadastro():
    if request.method == "POST":
        nome = request.form['nome']
        email = request.form['email']
        senha = sha256(request.form['senha'].encode('utf-8')).hexdigest()
        tipo = request.form['tipo']  # 'professor' ou 'aluno'
        create_user(nome, email, senha, tipo)
        return redirect(url_for('auth.login'))
    return render_template("cadastro.html")
@student_bp.route("/dashboard_aluno")
def dashboard_aluno():
    user_id = session.get("user")
    if not user_id:
        return redirect(url_for('auth.login'))  # Redireciona para login se não estiver logado

    user = find_user_by_id(user_id)  # Certifique-se de implementar essa função que busca o usuário pelo ID
    return render_template("dashboard_aluno.html", user=user)