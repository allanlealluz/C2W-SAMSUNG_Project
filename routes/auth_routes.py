from flask import Blueprint, render_template, request, redirect, url_for, session
from models import create_user, find_user
from hashlib import sha256
from models import find_user,create_user
auth_bp = Blueprint('auth', __name__)

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
        return render_template("errorPage.html")
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
@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
