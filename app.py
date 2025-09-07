from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import os, json, csv

app = Flask(__name__)

# ------------------- CONFIGURACIÓN SQLITE -------------------
basedir = os.path.abspath(os.path.dirname(__file__))
db_folder = os.path.join(basedir, "database")
os.makedirs(db_folder, exist_ok=True)  # crea la carpeta si no existe

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(db_folder, 'usuarios.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo de base de datos
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))

with app.app_context():
    db.create_all()


# ------------------- RUTAS BÁSICAS -------------------
@app.route('/')
def home():
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/usuario/<nombre>')
def usuario(nombre):
    return render_template("index.html", nombre=nombre)


# ------------------- TXT -------------------
@app.route("/guardar_txt", methods=["POST"])
def guardar_txt():
    dato = request.form.get("dato")
    os.makedirs("datos", exist_ok=True)
    with open("datos/datos.txt", "a") as f:
        f.write(dato + "\n")
    return redirect(url_for("home"))

@app.route("/leer_txt")
def leer_txt():
    archivo = "datos/datos.txt"
    if os.path.exists(archivo):
        with open(archivo, "r") as f:
            contenido = f.readlines()
    else:
        contenido = []
    return render_template("resultado.html", titulo="Datos desde TXT", datos=contenido)


# ------------------- JSON -------------------
@app.route("/guardar_json", methods=["POST"])
def guardar_json():
    dato = request.form.get("dato")
    os.makedirs("datos", exist_ok=True)
    archivo = "datos/datos.json"
    datos = []

    if os.path.exists(archivo) and os.stat(archivo).st_size > 0:
        with open(archivo, "r") as f:
            datos = json.load(f)

    datos.append({"dato": dato})

    with open(archivo, "w") as f:
        json.dump(datos, f, indent=4)

    return redirect(url_for("home"))

@app.route("/leer_json")
def leer_json():
    archivo = "datos/datos.json"
    if os.path.exists(archivo) and os.stat(archivo).st_size > 0:
        with open(archivo, "r") as f:
            datos = json.load(f)
    else:
        datos = []
    return jsonify(datos)


# ------------------- CSV -------------------
@app.route("/guardar_csv", methods=["POST"])
def guardar_csv():
    dato = request.form.get("dato")
    os.makedirs("datos", exist_ok=True)
    archivo = "datos/datos.csv"
    with open(archivo, "a", newline="") as f:
        escritor = csv.writer(f)
        escritor.writerow([dato])
    return redirect(url_for("home"))

@app.route("/leer_csv")
def leer_csv():
    archivo = "datos/datos.csv"
    datos = []
    if os.path.exists(archivo):
        with open(archivo, "r") as f:
            lector = csv.reader(f)
            for fila in lector:
                datos.append(fila)
    return render_template("resultado.html", titulo="Datos desde CSV", datos=datos)


# ------------------- SQLite -------------------
@app.route("/guardar_db", methods=["POST"])
def guardar_db():
    nombre = request.form.get("nombre")
    nuevo_usuario = Usuario(nombre=nombre)
    db.session.add(nuevo_usuario)
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/leer_db")
def leer_db():
    usuarios = Usuario.query.all()
    datos = [f"ID: {u.id} - Nombre: {u.nombre}" for u in usuarios]
    return render_template("resultado.html", titulo="Datos desde SQLite", datos=datos)


# ------------------- MAIN -------------------
if __name__ == '__main__':
    app.run(debug=True)
