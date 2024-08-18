from flask import Flask,render_template
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
        with app.open_resource('schema.sql',mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()
@app.route("/")
def index():
    return render_template("home.html")
  
@app.route("/initdb")
def initiate_database():
    init_db()
    return "DATABASE CONNECTED"
@app.route("/cadastro")
def cadastro():
    return render_template("cadastro.html")
@app.route("/login")
def login():
    return render_template("login.html")
if __name__ == "__main__":
    app.run(debug=True)

