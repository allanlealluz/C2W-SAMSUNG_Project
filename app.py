from flask import Flask
from routes.auth_routes import auth_bp
from routes.student_routes import student_bp
from routes.teacher_routes import teacher_bp 
from routes.admin_routes import admin_bp
from models import init_db

app = Flask(__name__)
app.secret_key = "aaaa"
app.config['DATABASE'] = 'database.db'

# Registro de Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(student_bp) 
app.register_blueprint(teacher_bp) 
app.register_blueprint(admin_bp)#tudo é executado aqui mesmo sendo tão reduzido o código

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
