from flask import Flask,render_template
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("home.html")
@app.route("/cadastro")
def cadastro():
    return render_template("cadastro.html")
if __name__ == "__main__":
    app.run(debug=True)

