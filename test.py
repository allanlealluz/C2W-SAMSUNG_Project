from flask import Flask,render_template
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("home.html")
@app.route("/cadastro/<nomes>")
def cadastro(nomes):
    return render_template("cadastro.html", nomes = nomes)
if __name__ == "__main__":
    app.run(debug=True)

